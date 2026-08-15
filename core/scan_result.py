# core/scan_result.py
from dataclasses import dataclass, field
from typing import List, Dict, Any

@dataclass
class ScanResult:
    target: str
    mode: str
    phases_completed: List[str] = field(default_factory=list)
    all_findings: List[Dict[str, Any]] = field(default_factory=list)
    report: Dict[str, Any] = field(default_factory=dict)
    error: str = ""
