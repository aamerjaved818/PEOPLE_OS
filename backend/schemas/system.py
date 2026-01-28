
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from . import org, core, auth, hcm

class InitialData(BaseModel):
    systemFlags: Optional[core.SystemFlags] = None
    payrollSettings: Optional[core.PayrollSettings] = None
    users: List[core.User] = []
    plants: List[org.Plant] = []
    departments: List[org.Department] = []
    subDepartments: List[org.SubDepartment] = []
    designations: List[org.Designation] = []
    grades: List[org.Grade] = []
    shifts: List[org.Shift] = []
    jobLevels: List[org.JobLevel] = []
    holidays: List[org.Holiday] = []
    banks: List[org.Bank] = []
    positions: List[org.Position] = []
    rolePermissions: Dict[str, List[str]] = {}
    currentUser: Optional[core.User] = None
