# ChatGPT tools, skills and execution playbook

ATLAS is managed via ChatGPT using the connected [GitHub repo](https://github.com/DoorBlox/atlas-omnifold-research) and explicit, user-approved research/Word/Google Docs actions. This is a research adaptation of [ORBIT's tool playbook](https://github.com/DoorBlox/orbit/blob/main/docs/CHATGPT_TOOL_PLAYBOOK.md).

| Task | Primary tool/workflow | Boundary |
| --- | --- | --- |
| Repos, branches, PRs, CI, provenance | Connected GitHub app | Confirm live main, exact PR head and actual checks; keep release manifest intact |
| Source-backed numerical and methods audit | Python plus source scripts, ATLAS paper and 2024 Zenodo data | Code passing does not validate experimental 2D covariance |
| Word manuscript, equations, captions, render QA | Container and installed `docx` skill | Verify selected author file hash, preserve tables/figures and inspect pages |
| School research plan and IMRAD/ARTICLE tabs | Connected Google Drive/Docs | Read actual tab, edit only by request, do not substitute the earlier ARTICLE for the latest DOCX |
| Scholarly literature and manuscript reviewer | Official publication sources, installed research/reviewer skills | Verify DOI metadata and source-to-claim support, flag uncertainties |
| Task continuity | [root handoff](../CHATGPT_HANDOFF.md), [AGENTS](../AGENTS.md), [CURRENT_STATE](CURRENT_STATE.md), [project history](PROJECT_HISTORY.md) | Update one checkpoint; no invisible background work |

Task-relevant skills may include `ecc-strategic-compact` for handoffs, `ecc-blueprint` for long research plans, `ecc-verification-loop` for source/test changes, `academic-humanizer` for academic clarity, `docx` for editable manuscripts and `asisten-reviewer-gra` for peer review. Verify availability and read the chosen skill's actual instructions; don't load every skill.

**Execution loop:** retrieve current state → select one READY work unit → identify exact source/hashes → perform bounded change → run targeted tests or Word visual QA → inspect diff/claims → GitHub PR for public source/docs only → verify exact-head CI → update current handoff and next action. Keep author's unpublished manuscript files private unless separately approved.
