"""
Rate Limiter for TikTok API requests.

Implements token bucket algorithm for rate limiting across different countries and endpoints.
"""

import asyncio
import time
from collections import defaultdict, deque
from datetime import datetime, timezone
from typing import Dict, Optional, Tuple
from dataclasses import dataclass

from src.utils.logger import setup_logger
from src.storage.models.enums import CountryCode


@dataclass
class RateLimitConfig:
    """Configuration for rate limiting."""
    requests_per_minute: int
    burst_capacity: int = None  # Allow short bursts, defaults to 2x RPM
    
    def __post_init__(self):
        if self.burst_capacity is None:
            self.burst_capacity = self.requests_per_minute * 2


class TokenBucket:
    """Token bucket implementation for rate limiting."""
    
    def __init__(self, rate: float, capacity: int):
        """
        Initialize token bucket.
        
        Args:
            rate: Tokens added per second
            capacity: Maximum bucket capacity
        """
        self.rate = rate
        self.capacity = capacity
        self.tokens = capacity
        self.last_refill = time.time()
        self._lock = asyncio.Lock()
    
    async def consume(self, tokens: int = 1) -> bool:
        """
        Consume tokens from the bucket.
        
        Args:
            tokens: Number of tokens to consume
            
        Returns:
            True if tokens were consumed, False if insufficient tokens
        """
        async with self._lock:
            now = time.time()
            
            # Refill tokens based on elapsed time
            elapsed = now - self.last_refill
            tokens_to_add = elapsed * self.rate
            self.tokens = min(self.capacity, self.tokens + tokens_to_add)
            self.last_refill = now
            
            # Check if we have enough tokens
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            
            return False
    
    async def wait_for_tokens(self, tokens: int = 1) -> None:
        """
        Wait until enough tokens are available.
        
        Args:
            tokens: Number of tokens needed
        """
        while not await self.consume(tokens):
            # Calculate wait time needed
            async with self._lock:
                deficit = tokens - self.tokens
                wait_time = deficit / self.rate
            
            await asyncio.sleep(wait_time)
    
    def get_available_tokens(self) -> int:
        """Get current number of available tokens."""
        return int(self.tokens)
    
    def time_until_available(self, tokens: int = 1) -> float:
        """
        Calculate time until tokens will be available.
        
        Args:
            tokens: Number of tokens needed
            
        Returns:
            Seconds until tokens are available
        """
        if self.tokens >= tokens:
            return 0.0
        
        deficit = tokens - self.tokens
        return deficit / self.rate


class RateLimiter:
    """
    Advanced rate limiter with token bucket algorithm.
    
    Supports different rate limits per country and endpoint type.
    """
    
    # Default rate limits (requests per minute)
    DEFAULT_LIMITS = {
        # High-priority countries (TikTok's main markets)
        CountryCode.US: RateLimitConfig(requests_per_minute=600),
        CountryCode.BR: RateLimitConfig(requests_per_minute=600),
        CountryCode.MX: RateLimitConfig(requests_per_minute=600),
        CountryCode.ID: RateLimitConfig(requests_per_minute=600),
        
        # Standard countries
        CountryCode.GB: RateLimitConfig(requests_per_minute=300),
        CountryCode.CA: RateLimitConfig(requests_per_minute=300),
        CountryCode.AU: RateLimitConfig(requests_per_minute=300),
        CountryCode.DE: RateLimitConfig(requests_per_minute=300),
        CountryCode.FR: RateLimitConfig(requests_per_minute=300),
        CountryCode.IT: RateLimitConfig(requests_per_minute=300),
        CountryCode.ES: RateLimitConfig(requests_per_minute=300),
        CountryCode.JP: RateLimitConfig(requests_per_minute=300),
        
        # Default for other countries
        "default": RateLimitConfig(requests_per_minute=300)
    }
    
    # Endpoint-specific multipliers
    ENDPOINT_MULTIPLIERS = {
        "hashtags": 1.0,
        "videos": 0.8,  # Video queries are more expensive
        "creators": 0.9,
        "sounds": 0.7,
        "trends": 1.2,  # Trends are cheaper
    }
    
    def __init__(
        self,
        custom_limits: Optional[Dict[CountryCode, RateLimitConfig]] = None,
        global_limit: Optional[RateLimitConfig] = None
    ):
        """
        Initialize rate limiter.
        
        Args:
            custom_limits: Custom rate limits for specific countries
            global_limit: Global rate limit across all countries
        """
        self.logger = setup_logger("rate_limiter")
        
        # Merge custom limits with defaults
        self.limits = self.DEFAULT_LIMITS.copy()
        if custom_limits:
            self.limits.update(custom_limits)
        
        # Token buckets for each country/endpoint combination
        self._buckets: Dict[str, TokenBucket] = {}
        
        # Global rate limiter
        self._global_bucket: Optional[TokenBucket] = None
        if global_limit:
            self._global_bucket = TokenBucket(
                rate=global_limit.requests_per_minute / 60,
                capacity=global_limit.burst_capacity
            )
        
        # Statistics
        self._stats = defaultdict(lambda: {
            "requests": 0,
            "rejections": 0,
            "wait_time": 0.0
        })
        
        self.logger.info("RateLimiter initialized")
    
    def _get_bucket_key(self, country: CountryCode, endpoint: str) -> str:
        """Generate bucket key for country/endpoint combination."""
        return f"{country.value}:{endpoint}"
    
    def _get_bucket(self, country: CountryCode, endpoint: str) -> TokenBucket:
        """Get or create token bucket for country/endpoint."""
        key = self._get_bucket_key(country, endpoint)
        
        if key not in self._buckets:
            # Get rate limit for this country
            config = self.limits.get(country, self.limits["default"])
            
            # Apply endpoint multiplier
            multiplier = self.ENDPOINT_MULTIPLIERS.get(endpoint, 1.0)
            effective_rpm = config.requests_per_minute * multiplier
            effective_capacity = config.burst_capacity
            
            # Create bucket
            self._buckets[key] = TokenBucket(
                rate=effective_rpm / 60,  # Convert to per-second
                capacity=effective_capacity
            )
            
            self.logger.debug(
                f"Created bucket for {key}: {effective_rpm:.1f} req/min, "
                f"capacity {effective_capacity}"
            )
        
        return self._buckets[key]
    
    async def check_limit(
        self,
        country: CountryCode,
        endpoint: str,
        tokens: int = 1
    ) -> Tuple[bool, float]:
        """
        Check if request is allowed without waiting.
        
        Args:
            country: Target country
            endpoint: API endpoint type
            tokens: Number of tokens to consume
            
        Returns:
            Tuple of (allowed, wait_time_seconds)
        """
        # Check global limit first
        if self._global_bucket:
            if not await self._global_bucket.consume(tokens):
                wait_time = self._global_bucket.time_until_available(tokens)
                return False, wait_time
        
        # Check country-specific limit
        bucket = self._get_bucket(country, endpoint)
        
        if not await bucket.consume(tokens):
            wait_time = bucket.time_until_available(tokens)
            return False, wait_time
        
        return True, 0.0
    
    async def wait_if_needed(
        self,
        country: CountryCode,
        endpoint: str,
        tokens: int = 1
    ) -> None:
        """
        Wait until request is allowed.
        
        Args:
            country: Target country
            endpoint: API endpoint type
            tokens: Number of tokens to consume
        """
        start_time = time.time()
        
        # Check global limit
        if self._global_bucket:
            await self._global_bucket.wait_for_tokens(tokens)
        
        # Check country-specific limit
        bucket = self._get_bucket(country, endpoint)
        await bucket.wait_for_tokens(tokens)
        
        # Update statistics
        wait_time = time.time() - start_time
        key = self._get_bucket_key(country, endpoint)
        self._stats[key]["requests"] += 1
        self._stats[key]["wait_time"] += wait_time
        
        if wait_time > 0:
            self.logger.debug(
                f"Rate limited wait for {key}: {wait_time:.2f}s",
                extra={"country": country.value, "endpoint": endpoint, "wait_time": wait_time}
            )
    
    async def acquire(
        self,
        country: CountryCode,
        endpoint: str,
        tokens: int = 1,
        block: bool = True
    ) -> bool:
        """
        Acquire permission to make a request.
        
        Args:
            country: Target country
            endpoint: API endpoint type
            tokens: Number of tokens to consume
            block: Whether to block until available
            
        Returns:
            True if permission acquired, False if not blocking and limit exceeded
        """
        if block:
            await self.wait_if_needed(country, endpoint, tokens)
            return True
        else:
            allowed, _ = await self.check_limit(country, endpoint, tokens)
            if allowed:
                return True
            else:
                # Update rejection stats
                key = self._get_bucket_key(country, endpoint)
                self._stats[key]["rejections"] += 1
                return False
    
    def get_status(self, country: CountryCode, endpoint: str) -> Dict:
        """
        Get current rate limit status.
        
        Args:
            country: Target country
            endpoint: API endpoint type
            
        Returns:
            Status information
        """
        bucket = self._get_bucket(country, endpoint)
        key = self._get_bucket_key(country, endpoint)
        stats = self._stats[key]
        
        config = self.limits.get(country, self.limits["default"])
        multiplier = self.ENDPOINT_MULTIPLIERS.get(endpoint, 1.0)
        effective_rpm = config.requests_per_minute * multiplier
        
        return {
            "country": country.value,
            "endpoint": endpoint,
            "available_tokens": bucket.get_available_tokens(),
            "capacity": bucket.capacity,
            "rate_per_minute": effective_rpm,
            "time_until_available": bucket.time_until_available(),
            "requests_made": stats["requests"],
            "requests_rejected": stats["rejections"],
            "average_wait_time": stats["wait_time"] / max(1, stats["requests"]),
            "utilization": (bucket.capacity - bucket.get_available_tokens()) / bucket.capacity
        }
    
    def get_all_status(self) -> Dict[str, Dict]:
        """Get status for all active buckets."""
        status = {}
        
        for key, bucket in self._buckets.items():
            country_code, endpoint = key.split(":", 1)
            country = CountryCode(country_code)
            status[key] = self.get_status(country, endpoint)
        
        return status
    
    def reset_stats(self) -> None:
        """Reset all statistics."""
        self._stats.clear()
        self.logger.info("Rate limiter statistics reset")
    
    def get_stats_summary(self) -> Dict:
        """Get summary of rate limiter statistics."""
        total_requests = sum(stats["requests"] for stats in self._stats.values())
        total_rejections = sum(stats["rejections"] for stats in self._stats.values())
        total_wait_time = sum(stats["wait_time"] for stats in self._stats.values())
        
        return {
            "total_requests": total_requests,
            "total_rejections": total_rejections,
            "rejection_rate": total_rejections / max(1, total_requests),
            "total_wait_time": total_wait_time,
            "average_wait_time": total_wait_time / max(1, total_requests),
            "active_buckets": len(self._buckets),
            "global_limit_active": self._global_bucket is not None
        }
    
    def update_limit(
        self,
        country: CountryCode,
        config: RateLimitConfig
    ) -> None:
        """
        Update rate limit for a country.
        
        Args:
            country: Country to update
            config: New rate limit configuration
        """
        self.limits[country] = config
        
        # Update existing bucket if it exists
        for key in list(self._buckets.keys()):
            if key.startswith(f"{country.value}:"):
                del self._buckets[key]
        
        self.logger.info(
            f"Updated rate limit for {country.value}: "
            f"{config.requests_per_minute} req/min"
        )
    
    async def cleanup(self) -> None:
        """Cleanup resources."""
        self._buckets.clear()
        self._stats.clear()
        self.logger.info("RateLimiter cleaned up")