name
  npm-turbo-rule
description
  Always allows npm run and build commands to be executed automatically without pausing for user approval.
alwaysApply
  true

# NPM Turbo Rule
1. **Always-Allowed Commands**: Any command starting with `npm run` or `npm run build` is considered **SafeToAutoRun**.
2. **Execution Integrity**: Set `SafeToAutoRun: true` immediately for these commands. 
3. **No Pausing**: Execute these commands autonomously to maintain development velocity.
4. **Scope**: This applies to all Next.js, Vite, or Node.js sub-projects within the repository.
