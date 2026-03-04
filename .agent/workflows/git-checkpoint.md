---
name: git-checkpoint
description: Autonomously creates safe rollback points in Git (Directive 16).
trigger: /checkpoint
---
# WORKFLOW: Version Control Hygiene
**Activation**: Triggered by `/checkpoint <optional: message>`
1. **Status Check**: Run `git status` to view uncommitted changes.
2. **Commit Generation**: Generate a strict Conventional Commit based on the diff. If it is exploratory work, use `chore(wip): checkpoint - <message>`.
3. **Tagging**: Create a timestamped Git tag: `git tag checkpoint-$(date +'%Y-%m-%d-%H%M')`.
4. **Deliverable**: Return the exact Git hash and rollback command (`git reset --hard <tag_name>`) to the Commander so their exploratory work is safely backed up.
