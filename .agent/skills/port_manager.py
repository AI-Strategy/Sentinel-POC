# .agent/skills/port_manager.py
import subprocess
from pydantic import BaseModel, Field

class PortManagerInput(BaseModel):
    target_port: int = Field(..., description="The port that needs to be freed (e.g., 3000, 8080).")

async def run(input_data: PortManagerInput) -> dict:
    """
    Enforces Port Discipline. 
    Instead of checking if a port is open and incrementing (3001, 3002...),
    this tool identifies the 'Zombie' process and kills it.
    """
    port = input_data.target_port
    
    try:
        # 1. Identify PID (Linux/MacOS lsof)
        # checks for process listening on the port
        cmd = f"lsof -t -i:{port}" 
        pid_bytes = subprocess.check_output(cmd, shell=True)
        pid = pid_bytes.decode().strip()

        if not pid:
            return {"status": "clean", "message": f"Port {port} is already free."}

        # 2. Kill the Zombie
        kill_cmd = f"kill -9 {pid}"
        subprocess.run(kill_cmd, shell=True, check=True)
        
        return {
            "status": "success", 
            "message": f"Killed zombie process {pid} on port {port}. Port is now available."
        }

    except subprocess.CalledProcessError:
        return {"status": "clean", "message": f"Port {port} is free (no process found)."}
    except Exception as e:
        return {"status": "error", "message": str(e)}
