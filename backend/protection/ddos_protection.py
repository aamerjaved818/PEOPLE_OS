"""
DDoS protection mechanisms for peopleOS eBusiness Suite API

Implements IP-based blocking, request pattern detection, and anomaly detection.
"""

from datetime import datetime, timedelta
from typing import Dict, Optional, Set, Tuple
from collections import defaultdict
from dataclasses import dataclass, field
import threading
from enum import Enum


class ThreatLevel(str, Enum):
    """DDoS threat levels"""
    SAFE = "safe"
    SUSPICIOUS = "suspicious"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class IPStats:
    """Statistics for an IP address"""
    ip_address: str
    request_count: int = 0
    error_count: int = 0
    blocked_requests: int = 0
    last_request: datetime = field(default_factory=datetime.utcnow)
    suspicious_patterns: int = 0
    threat_level: ThreatLevel = ThreatLevel.SAFE
    
    def get_error_rate(self) -> float:
        """Calculate error rate"""
        if self.request_count == 0:
            return 0.0
        return self.error_count / self.request_count
    
    def get_block_rate(self) -> float:
        """Calculate block rate"""
        total = self.request_count + self.blocked_requests
        if total == 0:
            return 0.0
        return self.blocked_requests / total


@dataclass
class DDoSConfig:
    """Configuration for DDoS protection"""
    # IP-based limits
    max_requests_per_ip_per_minute: int = 500
    max_requests_per_ip_per_hour: int = 10000
    
    # Error thresholds
    error_rate_threshold: float = 0.3  # 30% error rate
    error_count_threshold: int = 50
    
    # Blocking
    temporary_ban_duration: int = 300  # 5 minutes
    permanent_ban_after_violations: int = 5
    
    # Pattern detection
    slow_request_threshold: float = 5.0  # seconds
    suspicious_pattern_threshold: int = 10
    
    # Cleanup
    cleanup_interval: int = 300  # 5 minutes


class DDoSProtector:
    """Main DDoS protection system"""
    
    def __init__(self, config: Optional[DDoSConfig] = None):
        self.config = config or DDoSConfig()
        self.ip_stats: Dict[str, IPStats] = {}
        self.blocked_ips: Dict[str, datetime] = {}
        self.permanent_blacklist: Set[str] = set()
        self.lock = threading.RLock()
        self.last_cleanup = datetime.utcnow()
    
    def check_ip(self, ip_address: str) -> Tuple[bool, ThreatLevel, Optional[str]]:
        """Check if IP is allowed"""
        with self.lock:
            # Check permanent blacklist
            if ip_address in self.permanent_blacklist:
                return False, ThreatLevel.CRITICAL, "IP permanently banned"
            
            # Check temporary ban
            if ip_address in self.blocked_ips:
                ban_time = self.blocked_ips[ip_address]
                if datetime.utcnow() < ban_time:
                    remaining = int((ban_time - datetime.utcnow()).total_seconds())
                    return False, ThreatLevel.CRITICAL, f"Temporarily banned for {remaining} seconds"
                else:
                    # Ban expired
                    del self.blocked_ips[ip_address]
            
            # Get stats
            stats = self.ip_stats.get(ip_address)
            if stats:
                threat_level = stats.threat_level
                if threat_level == ThreatLevel.CRITICAL:
                    return False, threat_level, "Critical threat level detected"
                elif threat_level == ThreatLevel.WARNING:
                    return True, threat_level, "Warning: suspicious activity detected"
            
            return True, ThreatLevel.SAFE, None
    
    def record_request(self, ip_address: str, endpoint: str = "", response_time: float = 0.0):
        """Record successful request"""
        with self.lock:
            if ip_address not in self.ip_stats:
                self.ip_stats[ip_address] = IPStats(ip_address=ip_address)
            
            stats = self.ip_stats[ip_address]
            stats.request_count += 1
            stats.last_request = datetime.utcnow()
            
            # Check rate limits
            if stats.request_count > self.config.max_requests_per_ip_per_minute:
                self._escalate_threat_level(ip_address, ThreatLevel.SUSPICIOUS)
            
            if stats.request_count > self.config.max_requests_per_ip_per_hour:
                self._escalate_threat_level(ip_address, ThreatLevel.WARNING)
            
            # Check for slow requests (potential attack signature)
            if response_time > self.config.slow_request_threshold:
                stats.suspicious_patterns += 1
                if stats.suspicious_patterns > self.config.suspicious_pattern_threshold:
                    self._escalate_threat_level(ip_address, ThreatLevel.WARNING)
            
            self._cleanup_if_needed()
    
    def record_error(self, ip_address: str, error_type: str = ""):
        """Record failed request/error"""
        with self.lock:
            if ip_address not in self.ip_stats:
                self.ip_stats[ip_address] = IPStats(ip_address=ip_address)
            
            stats = self.ip_stats[ip_address]
            stats.error_count += 1
            
            # Check error rate
            if stats.get_error_rate() > self.config.error_rate_threshold:
                self._escalate_threat_level(ip_address, ThreatLevel.SUSPICIOUS)
            
            # Check absolute error count
            if stats.error_count > self.config.error_count_threshold:
                self._escalate_threat_level(ip_address, ThreatLevel.WARNING)
    
    def record_blocked_request(self, ip_address: str):
        """Record blocked request attempt"""
        with self.lock:
            if ip_address not in self.ip_stats:
                self.ip_stats[ip_address] = IPStats(ip_address=ip_address)
            
            stats = self.ip_stats[ip_address]
            stats.blocked_requests += 1
            
            # Multiple blocked requests indicate attack
            if stats.blocked_requests > self.config.error_count_threshold:
                self._escalate_threat_level(ip_address, ThreatLevel.CRITICAL)
                self._ban_ip_temporarily(ip_address)
    
    def _escalate_threat_level(self, ip_address: str, new_level: ThreatLevel):
        """Escalate threat level"""
        stats = self.ip_stats[ip_address]
        
        # Only escalate, don't downgrade
        if new_level.value > stats.threat_level.value:
            stats.threat_level = new_level
            
            # Apply automatic actions
            if new_level == ThreatLevel.CRITICAL:
                self._ban_ip_temporarily(ip_address)
                
                # Track violations
                if ip_address not in self.blocked_ips:
                    violation_count = sum(
                        1 for s in self.ip_stats.values()
                        if s.threat_level == ThreatLevel.CRITICAL
                        and (datetime.utcnow() - s.last_request).total_seconds() < 3600
                    )
                    
                    if violation_count >= self.config.permanent_ban_after_violations:
                        self.permanent_blacklist.add(ip_address)
    
    def _ban_ip_temporarily(self, ip_address: str):
        """Temporarily ban IP"""
        ban_until = datetime.utcnow() + timedelta(seconds=self.config.temporary_ban_duration)
        self.blocked_ips[ip_address] = ban_until
    
    def get_stats(self, ip_address: str) -> Optional[IPStats]:
        """Get statistics for IP"""
        with self.lock:
            return self.ip_stats.get(ip_address)
    
    def whitelist_ip(self, ip_address: str):
        """Whitelist an IP (remove from stats)"""
        with self.lock:
            self.ip_stats.pop(ip_address, None)
            self.blocked_ips.pop(ip_address, None)
            self.permanent_blacklist.discard(ip_address)
    
    def blacklist_ip(self, ip_address: str):
        """Permanently blacklist an IP"""
        with self.lock:
            self.permanent_blacklist.add(ip_address)
    
    def _cleanup_if_needed(self):
        """Clean up old statistics"""
        if (datetime.utcnow() - self.last_cleanup).total_seconds() < self.config.cleanup_interval:
            return
        
        with self.lock:
            cutoff = datetime.utcnow() - timedelta(hours=1)
            
            # Remove old stats
            to_remove = [
                ip for ip, stats in self.ip_stats.items()
                if (stats.last_request < cutoff and stats.threat_level == ThreatLevel.SAFE)
            ]
            for ip in to_remove:
                del self.ip_stats[ip]
            
            # Clean expired bans
            expired = [
                ip for ip, ban_time in self.blocked_ips.items()
                if ban_time < datetime.utcnow()
            ]
            for ip in expired:
                del self.blocked_ips[ip]
            
            self.last_cleanup = datetime.utcnow()
    
    def get_threat_summary(self) -> Dict[str, int]:
        """Get summary of threat levels"""
        with self.lock:
            summary = {
                "safe": 0,
                "suspicious": 0,
                "warning": 0,
                "critical": 0,
                "permanently_banned": len(self.permanent_blacklist),
                "temporarily_banned": len(self.blocked_ips)
            }
            
            for stats in self.ip_stats.values():
                summary[stats.threat_level.value] += 1
            
            return summary


# Global DDoS protector instance
_ddos_protector_instance: Optional[DDoSProtector] = None


def get_ddos_protector() -> DDoSProtector:
    """Get global DDoS protector instance"""
    global _ddos_protector_instance
    if _ddos_protector_instance is None:
        _ddos_protector_instance = DDoSProtector()
    return _ddos_protector_instance


def initialize_ddos_protection(config: Optional[DDoSConfig] = None) -> DDoSProtector:
    """Initialize DDoS protection"""
    global _ddos_protector_instance
    _ddos_protector_instance = DDoSProtector(config)
    return _ddos_protector_instance
