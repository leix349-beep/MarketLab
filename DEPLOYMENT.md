# Public Test Checklist

Use this checklist before publishing MarketLab as a public Streamlit Community Cloud app.

## Before upload

- [ ] Run every page in both English and Chinese.
- [ ] Confirm the app shows a useful message when market data is unavailable.
- [ ] Confirm no `.env`, `secrets.toml`, API key, account number or personal note is tracked.
- [ ] Keep generated `research_records/` data private unless a specific example is reviewed for publication.
- [ ] Add one screenshot and a short project description to the GitHub repository.
- [ ] Review the research disclaimer and limitations.

## GitHub

1. Create a new public repository named `marketlab`.
2. Upload the project source files, `pages/`, `tests/`, `README.md`, `ROADMAP.md`, `requirements.txt` and `.gitignore`.
3. Do not upload `.venv/`, `.env`, `.streamlit/secrets.toml` or generated research archives.
4. Check the GitHub file list once more before deployment.

## Streamlit Community Cloud

1. Sign in using the GitHub account that owns the repository.
2. Create a new app from the `marketlab` repository.
3. Set the entry point to `app.py`.
4. Deploy and test the public URL on a second browser or phone.
5. If a future feature needs credentials, place them in Streamlit app secrets, never in source code.

## Public-test acceptance criteria

- The landing page opens without an error.
- Each navigation item opens.
- Manual run buttons control expensive research tasks.
- English mode contains no unexplained Chinese table headings.
- Charts have labels, units and a visible benchmark.
- A failed data request does not erase the rest of the page.
- The disclaimer clearly states that outputs are historical research, not investment advice.

