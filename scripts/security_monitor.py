#!/usr/bin/env python3
"""
Real-time Security Monitoring and Alerting System
Monitors test execution, detects anomalies, and sends alerts
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from collections import deque
from pathlib import Path
import statistics
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import aiohttp
import yaml

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class Alert:
    """Security alert data structure"""
    severity: str  # critical, high, medium, low
    type: str  # anomaly, threshold, pattern, failure
    message: str
    details: Dict[str, Any]
    timestamp: datetime
    test_id: Optional[str] = None
    model: Optional[str] = None
    probe: Optional[str] = None


class SecurityMonitor:
    """Real-time security monitoring system"""
    
    def __init__(self, config_path: str = "configs/monitor.yaml"):
        self.config = self._load_config(config_path)
        self.alerts_queue = deque(maxlen=1000)
        self.metrics_history = deque(maxlen=10000)
        self.baseline_metrics = {}
        self.anomaly_threshold = 2.5  # Standard deviations
        self.alert_handlers = []
        self.running = False
        
    def _load_config(self, config_path: str) -> dict:
        """Load monitoring configuration"""
        if Path(config_path).exists():
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        return {
            "monitoring": {
                "interval": 5,
                "alert_cooldown": 60,
                "metrics_retention": 3600
            },
            "thresholds": {
                "success_rate_min": 0.85,
                "response_time_max": 2000,
                "vulnerability_rate_max": 0.15,
                "concurrent_attacks_max": 10
            },
            "notifications": {
                "email": {"enabled": False},
                "slack": {"enabled": False},
                "webhook": {"enabled": False}
            }
        }
    
    async def start_monitoring(self):
        """Start the monitoring system"""
        self.running = True
        logger.info("Security monitoring started")
        
        # Start background tasks
        tasks = [
            asyncio.create_task(self._collect_metrics()),
            asyncio.create_task(self._analyze_patterns()),
            asyncio.create_task(self._process_alerts()),
            asyncio.create_task(self._update_baseline())
        ]
        
        try:
            await asyncio.gather(*tasks)
        except KeyboardInterrupt:
            self.running = False
            logger.info("Security monitoring stopped")
    
    async def _collect_metrics(self):
        """Continuously collect security metrics"""
        while self.running:
            try:
                metrics = await self._fetch_current_metrics()
                self.metrics_history.append({
                    'timestamp': datetime.now(),
                    'data': metrics
                })
                
                # Check thresholds
                await self._check_thresholds(metrics)
                
                # Detect anomalies
                await self._detect_anomalies(metrics)
                
            except Exception as e:
                logger.error(f"Error collecting metrics: {e}")
            
            await asyncio.sleep(self.config['monitoring']['interval'])
    
    async def _fetch_current_metrics(self) -> dict:
        """Fetch current metrics from the application"""
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get('http://localhost:7000/api/metrics') as resp:
                    return await resp.json()
            except:
                return {}
    
    async def _check_thresholds(self, metrics: dict):
        """Check if metrics exceed configured thresholds"""
        thresholds = self.config['thresholds']
        
        # Check success rate
        if metrics.get('success_rate', 1) < thresholds['success_rate_min']:
            await self._create_alert(
                severity='high',
                type='threshold',
                message=f"Success rate below threshold: {metrics['success_rate']:.2%}",
                details={'metric': 'success_rate', 'value': metrics['success_rate']}
            )
        
        # Check response time
        if metrics.get('avg_response_time', 0) > thresholds['response_time_max']:
            await self._create_alert(
                severity='medium',
                type='threshold',
                message=f"Response time exceeds threshold: {metrics['avg_response_time']}ms",
                details={'metric': 'response_time', 'value': metrics['avg_response_time']}
            )
        
        # Check vulnerability rate
        vuln_rate = metrics.get('vulnerability_rate', 0)
        if vuln_rate > thresholds['vulnerability_rate_max']:
            await self._create_alert(
                severity='critical',
                type='threshold',
                message=f"High vulnerability detection rate: {vuln_rate:.2%}",
                details={'metric': 'vulnerability_rate', 'value': vuln_rate}
            )
    
    async def _detect_anomalies(self, metrics: dict):
        """Detect statistical anomalies in metrics"""
        if len(self.metrics_history) < 100:
            return  # Need sufficient history for baseline
        
        for key, value in metrics.items():
            if key in self.baseline_metrics and isinstance(value, (int, float)):
                baseline = self.baseline_metrics[key]
                z_score = abs((value - baseline['mean']) / baseline['std'])
                
                if z_score > self.anomaly_threshold:
                    await self._create_alert(
                        severity='medium',
                        type='anomaly',
                        message=f"Anomaly detected in {key}: {value} (z-score: {z_score:.2f})",
                        details={
                            'metric': key,
                            'value': value,
                            'z_score': z_score,
                            'baseline_mean': baseline['mean'],
                            'baseline_std': baseline['std']
                        }
                    )
    
    async def _analyze_patterns(self):
        """Analyze patterns in security events"""
        while self.running:
            try:
                # Detect attack patterns
                recent_metrics = list(self.metrics_history)[-100:]
                if recent_metrics:
                    await self._detect_attack_patterns(recent_metrics)
                    await self._detect_escalation_patterns(recent_metrics)
                    await self._detect_timing_patterns(recent_metrics)
            except Exception as e:
                logger.error(f"Error analyzing patterns: {e}")
            
            await asyncio.sleep(30)  # Analyze every 30 seconds
    
    async def _detect_attack_patterns(self, metrics: List[dict]):
        """Detect coordinated attack patterns"""
        # Look for simultaneous spikes in different attack types
        attack_counts = {}
        for m in metrics[-20:]:  # Last 20 samples
            data = m.get('data', {})
            for attack_type in ['prompt_injection', 'data_leakage', 'dos', 'model_manipulation']:
                count = data.get(f'{attack_type}_attempts', 0)
                if attack_type not in attack_counts:
                    attack_counts[attack_type] = []
                attack_counts[attack_type].append(count)
        
        # Check for coordinated attacks
        simultaneous_attacks = 0
        for i in range(len(attack_counts.get('prompt_injection', []))):
            attacks_at_time = sum(1 for at in attack_counts.values() if i < len(at) and at[i] > 0)
            if attacks_at_time >= 3:
                simultaneous_attacks += 1
        
        if simultaneous_attacks > 5:
            await self._create_alert(
                severity='critical',
                type='pattern',
                message="Coordinated attack pattern detected",
                details={'simultaneous_attack_count': simultaneous_attacks}
            )
    
    async def _detect_escalation_patterns(self, metrics: List[dict]):
        """Detect escalating attack severity"""
        severity_timeline = []
        for m in metrics[-50:]:
            data = m.get('data', {})
            severity_score = (
                data.get('critical_vulns', 0) * 4 +
                data.get('high_vulns', 0) * 3 +
                data.get('medium_vulns', 0) * 2 +
                data.get('low_vulns', 0) * 1
            )
            severity_timeline.append(severity_score)
        
        if len(severity_timeline) >= 10:
            # Check for increasing trend
            recent_avg = statistics.mean(severity_timeline[-5:])
            older_avg = statistics.mean(severity_timeline[-10:-5])
            
            if recent_avg > older_avg * 1.5:  # 50% increase
                await self._create_alert(
                    severity='high',
                    type='pattern',
                    message="Escalating attack severity detected",
                    details={
                        'recent_severity': recent_avg,
                        'previous_severity': older_avg,
                        'increase_percentage': ((recent_avg - older_avg) / older_avg) * 100
                    }
                )
    
    async def _detect_timing_patterns(self, metrics: List[dict]):
        """Detect timing-based attack patterns"""
        timestamps = [m['timestamp'] for m in metrics[-100:]]
        if len(timestamps) < 2:
            return
        
        # Calculate inter-arrival times
        intervals = []
        for i in range(1, len(timestamps)):
            interval = (timestamps[i] - timestamps[i-1]).total_seconds()
            intervals.append(interval)
        
        if intervals:
            avg_interval = statistics.mean(intervals)
            std_interval = statistics.stdev(intervals) if len(intervals) > 1 else 0
            
            # Detect regular automated attacks
            if std_interval < avg_interval * 0.1:  # Very regular timing
                await self._create_alert(
                    severity='medium',
                    type='pattern',
                    message="Automated attack pattern detected (regular timing)",
                    details={
                        'average_interval': avg_interval,
                        'std_deviation': std_interval
                    }
                )
    
    async def _update_baseline(self):
        """Update baseline metrics for anomaly detection"""
        while self.running:
            try:
                if len(self.metrics_history) >= 100:
                    # Calculate baseline statistics
                    metrics_data = [m['data'] for m in list(self.metrics_history)[-500:]]
                    
                    for key in metrics_data[0].keys():
                        values = [m.get(key, 0) for m in metrics_data if isinstance(m.get(key), (int, float))]
                        if values:
                            self.baseline_metrics[key] = {
                                'mean': statistics.mean(values),
                                'std': statistics.stdev(values) if len(values) > 1 else 1,
                                'min': min(values),
                                'max': max(values)
                            }
            except Exception as e:
                logger.error(f"Error updating baseline: {e}")
            
            await asyncio.sleep(300)  # Update every 5 minutes
    
    async def _create_alert(self, severity: str, type: str, message: str, details: dict):
        """Create and queue a security alert"""
        alert = Alert(
            severity=severity,
            type=type,
            message=message,
            details=details,
            timestamp=datetime.now()
        )
        
        # Check for duplicate alerts (cooldown period)
        recent_alerts = [a for a in self.alerts_queue 
                        if (datetime.now() - a.timestamp).seconds < self.config['monitoring']['alert_cooldown']]
        
        if not any(a.message == alert.message for a in recent_alerts):
            self.alerts_queue.append(alert)
            logger.warning(f"ALERT [{severity.upper()}]: {message}")
            
            # Trigger notification handlers
            for handler in self.alert_handlers:
                await handler(alert)
    
    async def _process_alerts(self):
        """Process and handle queued alerts"""
        while self.running:
            try:
                # Group alerts by severity
                critical_alerts = [a for a in self.alerts_queue if a.severity == 'critical']
                high_alerts = [a for a in self.alerts_queue if a.severity == 'high']
                
                # Send notifications for critical alerts
                if critical_alerts:
                    await self._send_notifications(critical_alerts)
                
                # Log alert summary
                if len(self.alerts_queue) > 0:
                    logger.info(f"Alert Summary - Critical: {len(critical_alerts)}, "
                              f"High: {len(high_alerts)}, Total: {len(self.alerts_queue)}")
                
            except Exception as e:
                logger.error(f"Error processing alerts: {e}")
            
            await asyncio.sleep(60)  # Process every minute
    
    async def _send_notifications(self, alerts: List[Alert]):
        """Send notifications for critical alerts"""
        if self.config['notifications']['webhook']['enabled']:
            webhook_url = self.config['notifications']['webhook']['url']
            async with aiohttp.ClientSession() as session:
                payload = {
                    'alerts': [
                        {
                            'severity': a.severity,
                            'message': a.message,
                            'timestamp': a.timestamp.isoformat(),
                            'details': a.details
                        }
                        for a in alerts
                    ]
                }
                try:
                    await session.post(webhook_url, json=payload)
                except Exception as e:
                    logger.error(f"Failed to send webhook notification: {e}")
    
    def get_alert_summary(self) -> dict:
        """Get summary of current alerts"""
        return {
            'total_alerts': len(self.alerts_queue),
            'critical': len([a for a in self.alerts_queue if a.severity == 'critical']),
            'high': len([a for a in self.alerts_queue if a.severity == 'high']),
            'medium': len([a for a in self.alerts_queue if a.severity == 'medium']),
            'low': len([a for a in self.alerts_queue if a.severity == 'low']),
            'recent_alerts': [
                {
                    'severity': a.severity,
                    'type': a.type,
                    'message': a.message,
                    'timestamp': a.timestamp.isoformat()
                }
                for a in list(self.alerts_queue)[-10:]
            ]
        }


async def main():
    """Main entry point"""
    monitor = SecurityMonitor()
    
    # Add custom alert handler
    async def custom_handler(alert: Alert):
        if alert.severity == 'critical':
            # Add your custom logic here (e.g., shut down system, block IP, etc.)
            logger.critical(f"CRITICAL SECURITY EVENT: {alert.message}")
    
    monitor.alert_handlers.append(custom_handler)
    
    # Start monitoring
    await monitor.start_monitoring()


if __name__ == "__main__":
    asyncio.run(main())
