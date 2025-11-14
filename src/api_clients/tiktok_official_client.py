"""
TikTok Official API Client

Handles communication with the TikTok Official API for data collection.
"""

import asyncio
import json
import time
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

import aiohttp
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from src.utils.logger import setup_logger
from src.storage.models.enums import CountryCode, NicheType, DataSourceType


@dataclass
class TikTokAPIError(Exception):
    """Base exception for TikTok API errors."""
    message: str
    status_code: Optional[int] = None
    response_data: Optional[Dict] = None


@dataclass
class RateLimitError(TikTokAPIError):
    """Exception raised when rate limit is exceeded."""
    retry_after: Optional[int] = None


@dataclass
class AuthenticationError(TikTokAPIError):
    """Exception raised when authentication fails."""
    pass


class CircuitBreaker:
    """Circuit breaker pattern for API calls."""
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
        
    def call_allowed(self) -> bool:
        """Check if API call is allowed based on circuit state."""
        if self.state == "CLOSED":
            return True
        elif self.state == "OPEN":
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = "HALF_OPEN"
                return True
            return False
        else:  # HALF_OPEN
            return True
    
    def record_success(self):
        """Record successful API call."""
        self.failure_count = 0
        self.state = "CLOSED"
    
    def record_failure(self):
        """Record failed API call."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"


class TikTokAPIClient:
    """Robust client for TikTok Official API with OAuth2 authentication."""
    
    # Rate limits per country (requests per minute)
    RATE_LIMITS = {
        CountryCode.US: 600,
        CountryCode.BR: 600,
        CountryCode.MX: 600,
        CountryCode.ID: 600,
        # Default for other countries
        "default": 300
    }
    
    # API endpoints
    BASE_URL = "https://open.tiktokapis.com/v2"
    TOKEN_URL = f"{BASE_URL}/oauth/token"
    HASHTAGS_URL = f"{BASE_URL}/research/hashtag/"
    VIDEO_URL = f"{BASE_URL}/video/query/"
    CREATOR_URL = f"{BASE_URL}/user/info/"
    SOUND_URL = f"{BASE_URL}/music/query/"
    
    def __init__(
        self,
        client_key: str,
        client_secret: str,
        region: str = "US",
        timeout: int = 30,
        max_retries: int = 3
    ):
        """
        Initialize TikTok API client.
        
        Args:
            client_key: TikTok API client key
            client_secret: TikTok API client secret
            region: API region (default: US)
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries for failed requests
        """
        self.client_key = client_key
        self.client_secret = client_secret
        self.region = region.upper()
        self.timeout = timeout
        self.max_retries = max_retries
        
        self.logger = setup_logger("tiktok_api_client")
        
        # Token management
        self._access_token = None
        self._token_expires_at = None
        
        # Rate limiting
        self._rate_limits = {}  # country -> (requests, window_start)
        
        # Circuit breaker for each endpoint
        self._circuit_breakers = {
            "auth": CircuitBreaker(),
            "hashtags": CircuitBreaker(),
            "video": CircuitBreaker(),
            "creator": CircuitBreaker(),
            "sound": CircuitBreaker()
        }
        
        # HTTP session with retry strategy
        self._session = self._create_session()
        
        # Async session
        self._async_session = None
        
        self.logger.info(f"TikTokAPIClient initialized for region {self.region}")
    
    def _create_session(self) -> requests.Session:
        """Create HTTP session with retry strategy."""
        session = requests.Session()
        
        retry_strategy = Retry(
            total=self.max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session
    
    async def _get_async_session(self) -> aiohttp.ClientSession:
        """Get or create async HTTP session."""
        if self._async_session is None or self._async_session.closed:
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            self._async_session = aiohttp.ClientSession(timeout=timeout)
        return self._async_session
    
    def _get_rate_limit(self, country: CountryCode) -> int:
        """Get rate limit for a country."""
        return self.RATE_LIMITS.get(country, self.RATE_LIMITS["default"])
    
    async def _check_rate_limit(self, country: CountryCode) -> None:
        """Check and enforce rate limiting."""
        rate_limit = self._get_rate_limit(country)
        now = time.time()
        window_start = int(now // 60) * 60  # Start of current minute
        
        if country not in self._rate_limits:
            self._rate_limits[country] = (0, window_start)
        
        requests_count, last_window = self._rate_limits[country]
        
        # Reset window if we're in a new minute
        if window_start != last_window:
            requests_count = 0
            self._rate_limits[country] = (0, window_start)
        
        # Check if we've exceeded the limit
        if requests_count >= rate_limit:
            wait_time = 60 - (now % 60)  # Seconds until next minute
            self.logger.warning(
                f"Rate limit exceeded for {country}, waiting {wait_time:.1f}s"
            )
            await asyncio.sleep(wait_time)
            self._rate_limits[country] = (0, window_start)
        else:
            # Increment counter
            self._rate_limits[country] = (requests_count + 1, window_start)
    
    async def get_access_token(self) -> str:
        """
        Get OAuth2 access token with caching and refresh.
        
        Returns:
            Valid access token
        """
        # Check if we have a valid cached token
        if (
            self._access_token 
            and self._token_expires_at 
            and datetime.now(timezone.utc) < self._token_expires_at
        ):
            return self._access_token
        
        # Check circuit breaker
        if not self._circuit_breakers["auth"].call_allowed():
            raise TikTokAPIError("Authentication circuit breaker is open")
        
        try:
            session = await self._get_async_session()
            
            payload = {
                "client_key": self.client_key,
                "client_secret": self.client_secret,
                "grant_type": "client_credentials"
            }
            
            async with session.post(
                self.TOKEN_URL,
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                data = await response.json()
                
                if response.status == 200:
                    self._access_token = data["access_token"]
                    expires_in = data.get("expires_in", 3600)
                    self._token_expires_at = datetime.now(timezone.utc).replace(
                        microsecond=0
                    ) + timedelta(seconds=expires_in - 300)  # Refresh 5min early
                    
                    self._circuit_breakers["auth"].record_success()
                    self.logger.info("Access token refreshed successfully")
                    
                    return self._access_token
                else:
                    error_msg = data.get("message", "Authentication failed")
                    self._circuit_breakers["auth"].record_failure()
                    raise AuthenticationError(error_msg, response.status, data)
                    
        except Exception as e:
            self._circuit_breakers["auth"].record_failure()
            self.logger.error(f"Failed to get access token: {str(e)}")
            raise
    
    async def _make_request(
        self,
        endpoint: str,
        method: str = "GET",
        data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> Dict:
        """
        Make authenticated request to TikTok API.
        
        Args:
            endpoint: API endpoint
            method: HTTP method
            data: Request body data
            params: URL parameters
            
        Returns:
            Response data
        """
        # Determine circuit breaker for this endpoint
        cb_name = "auth" if "token" in endpoint else "hashtags"
        if "video" in endpoint:
            cb_name = "video"
        elif "user" in endpoint:
            cb_name = "creator"
        elif "music" in endpoint:
            cb_name = "sound"
        
        circuit_breaker = self._circuit_breakers[cb_name]
        
        if not circuit_breaker.call_allowed():
            raise TikTokAPIError(f"Circuit breaker open for {cb_name}")
        
        # Get access token
        token = await self.get_access_token()
        
        try:
            session = await self._get_async_session()
            
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            async with session.request(
                method,
                endpoint,
                json=data,
                params=params,
                headers=headers
            ) as response:
                response_data = await response.json()
                
                # Handle rate limiting
                if response.status == 429:
                    retry_after = response.headers.get("X-RateLimit-Reset")
                    raise RateLimitError(
                        "Rate limit exceeded",
                        response.status,
                        response_data,
                        int(retry_after) if retry_after else None
                    )
                
                # Handle other errors
                if response.status >= 400:
                    error_msg = response_data.get("message", "API request failed")
                    circuit_breaker.record_failure()
                    raise TikTokAPIError(error_msg, response.status, response_data)
                
                circuit_breaker.record_success()
                return response_data
                
        except aiohttp.ClientError as e:
            circuit_breaker.record_failure()
            self.logger.error(f"HTTP error in request to {endpoint}: {str(e)}")
            raise TikTokAPIError(f"HTTP error: {str(e)}")
        except Exception as e:
            circuit_breaker.record_failure()
            self.logger.error(f"Unexpected error in request to {endpoint}: {str(e)}")
            raise
    
    async def query_hashtags(
        self,
        country: CountryCode,
        niche: Optional[NicheType] = None,
        limit: int = 50
    ) -> List[Dict]:
        """
        Query trending hashtags for a country.
        
        Args:
            country: Country code
            niche: Optional niche filter
            limit: Maximum number of hashtags to return
            
        Returns:
            List of hashtag data
        """
        await self._check_rate_limit(country)
        
        params = {
            "country": country.value,
            "max_count": min(limit, 100)  # API limit
        }
        
        if niche:
            params["niche"] = niche.value
        
        try:
            response = await self._make_request(
                self.HASHTAGS_URL,
                params=params
            )
            
            hashtags = response.get("data", {}).get("hashtags", [])
            
            self.logger.info(
                f"Retrieved {len(hashtags)} hashtags for {country}",
                extra={"country": country.value, "niche": niche.value if niche else None}
            )
            
            return hashtags
            
        except Exception as e:
            self.logger.error(f"Failed to query hashtags for {country}: {str(e)}")
            raise
    
    async def get_video_info(self, video_id: str) -> Dict:
        """
        Get detailed information for a specific video.
        
        Args:
            video_id: TikTok video ID
            
        Returns:
            Video information
        """
        params = {"video_id": video_id}
        
        try:
            response = await self._make_request(
                self.VIDEO_URL,
                params=params
            )
            
            video_data = response.get("data", {})
            
            self.logger.info(
                f"Retrieved video info for {video_id}",
                extra={"video_id": video_id}
            )
            
            return video_data
            
        except Exception as e:
            self.logger.error(f"Failed to get video info for {video_id}: {str(e)}")
            raise
    
    async def get_creator_info(self, creator_id: str) -> Dict:
        """
        Get detailed information for a specific creator.
        
        Args:
            creator_id: TikTok creator ID
            
        Returns:
            Creator information
        """
        params = {"user_id": creator_id}
        
        try:
            response = await self._make_request(
                self.CREATOR_URL,
                params=params
            )
            
            creator_data = response.get("data", {})
            
            self.logger.info(
                f"Retrieved creator info for {creator_id}",
                extra={"creator_id": creator_id}
            )
            
            return creator_data
            
        except Exception as e:
            self.logger.error(f"Failed to get creator info for {creator_id}: {str(e)}")
            raise
    
    async def get_sound_info(self, sound_id: str) -> Dict:
        """
        Get detailed information for a specific sound.
        
        Args:
            sound_id: TikTok sound ID
            
        Returns:
            Sound information
        """
        params = {"music_id": sound_id}
        
        try:
            response = await self._make_request(
                self.SOUND_URL,
                params=params
            )
            
            sound_data = response.get("data", {})
            
            self.logger.info(
                f"Retrieved sound info for {sound_id}",
                extra={"sound_id": sound_id}
            )
            
            return sound_data
            
        except Exception as e:
            self.logger.error(f"Failed to get sound info for {sound_id}: {str(e)}")
            raise
    
    async def close(self):
        """Close async session and cleanup resources."""
        if self._async_session and not self._async_session.closed:
            await self._async_session.close()
        
        if self._session:
            self._session.close()
        
        self.logger.info("TikTokAPIClient closed")
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()


# Compatibility alias for existing code
TikTokOfficialClient = TikTokAPIClient


from datetime import timedelta