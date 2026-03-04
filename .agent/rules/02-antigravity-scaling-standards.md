name
  antigravity-scaling-standards
description
  Engineering standards for scaling, modularity, and tool usage.
alwaysApply
  true

# Engineering Scaling Laws
1. **Skills over Scripts**: Favor atomic, reusable tools in `.agent/skills/` over monolithic script blocks.
2. **Version Control Hygiene**: For all major changes using "Deep Research" or "Canvas" modes, you must increment the internal version in the file header.
3. **Automated Documentation**: Every new function or module must be accompanied by updated markdown documentation in `/docs`. Undocumented code is considered broken code.
4. **Anti-Downgrade Protection**: You are **FORBIDDEN** from downgrading libraries/languages to resolve conflicts. Fix the code to work with the current stable release.
