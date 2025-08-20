import json
from datetime import timedelta
from typing import Dict, List


class OutputFormatter:
    """Output formatting utilities for consistent CLI display."""
    
    @staticmethod
    def format_uptime(seconds: int) -> str:
        """Format uptime in human-readable format."""
        if isinstance(seconds, timedelta):
            seconds = int(seconds.total_seconds())
        
        if seconds < 60:
            return f"{seconds}s"
        elif seconds < 3600:
            minutes = seconds // 60
            return f"{minutes}m"
        elif seconds < 86400:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            return f"{hours}h {minutes}m"
        else:
            days = seconds // 86400
            hours = (seconds % 86400) // 3600
            return f"{days}d {hours}h"
    
    @staticmethod
    def format_memory_usage(bytes_value: int) -> str:
        """Format memory usage with appropriate units."""
        if isinstance(bytes_value, str):
            # Handle string inputs like "256M", "2GB"
            bytes_value = bytes_value.upper()
            if bytes_value.endswith('K'):
                return bytes_value.replace('K', 'KB')
            elif bytes_value.endswith('M'):
                return bytes_value.replace('M', 'MB')
            elif bytes_value.endswith('G'):
                return bytes_value.replace('G', 'GB')
            return bytes_value
        
        # Convert bytes to appropriate unit
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_value < 1024.0:
                return f"{bytes_value:.1f}{unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.1f}PB"
    
    @staticmethod
    def format_url_table(urls: List[Dict]) -> str:
        """Format URLs in aligned table format."""
        if not urls:
            return "No URLs available"
        
        # Calculate column widths
        name_width = max(len(url.get('name', '')) for url in urls)
        url_width = max(len(url.get('url', '')) for url in urls)
        
        # Minimum widths
        name_width = max(name_width, 10)
        url_width = max(url_width, 20)
        
        lines = []
        for url in urls:
            name = url.get('name', '').ljust(name_width)
            url_str = url.get('url', '').ljust(url_width)
            description = url.get('description', '')
            
            if description:
                lines.append(f"  → {name}: {url_str} - {description}")
            else:
                lines.append(f"  → {name}: {url_str}")
        
        return '\n'.join(lines)
    
    @staticmethod
    def colorize_status(status: str) -> str:
        """Apply status indicators without emojis."""
        status_map = {
            'running': '[OK]',
            'stopped': '[STOPPED]',
            'ready': '[OK]',
            'error': '[ERROR]',
            'warning': '[WARN]'
        }
        return status_map.get(status.lower(), status)
    
    @staticmethod
    def format_json_output(data: Dict) -> str:
        """Format data as pretty JSON."""
        return json.dumps(data, indent=2, sort_keys=True)
    
    @staticmethod
    def format_progress_bar(current: int, total: int, width: int = 20) -> str:
        """Create progress bar for operations."""
        if total == 0:
            return "[" + "?" * width + "]"
        
        progress = current / total
        filled = int(width * progress)
        bar = "█" * filled + "░" * (width - filled)
        percentage = int(progress * 100)
        
        return f"[{bar}] {percentage}%"
    
    @staticmethod
    def format_warning_box(message: str) -> str:
        """Format warning messages with box drawing."""
        lines = message.split('\n')
        max_width = max(len(line) for line in lines) if lines else 0
        box_width = max_width + 4
        
        result = []
        result.append("┌" + "─" * (box_width - 2) + "┐")
        
        for line in lines:
            padded_line = f"│ {line.ljust(max_width)} │"
            result.append(padded_line)
        
        result.append("└" + "─" * (box_width - 2) + "┘")
        
        return '\n'.join(result)
    
    @staticmethod
    def format_table(headers: List[str], rows: List[List[str]]) -> str:
        """Format data as aligned table."""
        if not headers or not rows:
            return ""
        
        # Calculate column widths
        col_widths = [len(header) for header in headers]
        
        for row in rows:
            for i, cell in enumerate(row):
                if i < len(col_widths):
                    col_widths[i] = max(col_widths[i], len(str(cell)))
        
        # Format header
        header_line = " | ".join(header.ljust(col_widths[i]) for i, header in enumerate(headers))
        separator = "-+-".join("-" * width for width in col_widths)
        
        # Format rows
        formatted_rows = []
        for row in rows:
            formatted_row = " | ".join(
                str(cell).ljust(col_widths[i]) 
                for i, cell in enumerate(row)
            )
            formatted_rows.append(formatted_row)
        
        # Combine all parts
        result = [header_line, separator] + formatted_rows
        return '\n'.join(result)
    
    @staticmethod
    def format_service_status(services: List[Dict]) -> str:
        """Format service status information."""
        if not services:
            return "No services running"
        
        lines = []
        for service in services:
            name = service.get('name', 'unknown')
            status = service.get('status', 'unknown')
            service_type = service.get('type', '')
            
            status_icon = OutputFormatter.colorize_status(status)
            type_info = f" ({service_type})" if service_type else ""
            
            lines.append(f"  {status_icon} {name}{type_info} - {status.title()}")
        
        return '\n'.join(lines)
    
    @staticmethod
    def format_stack_summary(stack_info: Dict) -> str:
        """Format stack summary information."""
        lines = []
        
        # Stack name and uptime
        name = stack_info.get('name', 'Unknown')
        uptime = stack_info.get('uptime')
        if uptime:
            uptime_str = OutputFormatter.format_uptime(uptime)
            lines.append(f"{name} (running {uptime_str})")
        else:
            lines.append(name)
        
        # Access URL
        access_url = stack_info.get('access_url')
        if access_url:
            lines.append(f"    {access_url}")
        
        # Container count
        containers = stack_info.get('containers', {})
        running_count = sum(1 for status in containers.values() if status == 'running')
        total_count = len(containers)
        lines.append(f"    {running_count}/{total_count} containers running")
        
        # Memory usage
        memory = stack_info.get('memory_usage')
        if memory:
            lines.append(f"    Memory usage: {memory}")
        
        return '\n'.join(lines)