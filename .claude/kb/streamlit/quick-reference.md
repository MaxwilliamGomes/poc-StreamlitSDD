# Streamlit Quick Reference

> Fast lookup tables. For code examples, see linked files.
> **MCP Validated**: 2026-11-01 (official docs via WebFetch; Context7/Exa unavailable)
> **Build Confirmed**: 2026-11-02 (Streamlit 1.66.1, Plotly 7.1.0, pandas 3.1.0, in the browser)

## Core Signatures (1.66.0)

| API | Key arguments | Notes |
|-----|---------------|-------|
| `st.cache_data` | `ttl, max_entries, show_spinner, persist, scope, refresh_mode` | `ttl` defaults to `None` (never expires); ignored when `persist` is on |
| `st.cache_resource` | `ttl, max_entries, validate, on_release, scope` | Returns one shared object, which must be thread-safe |
| `st.connection` | `name, type, max_entries, ttl, **kwargs` | Kwargs override `secrets.toml` |
| `conn.query` | `sql, *, ttl, params, show_spinner, chunksize` | Binds `:name`; default `ttl=None` caches forever |
| `st.metric` | `label, value, delta, delta_color, border, chart_data, delta_arrow, delta_description` | `value` may be a preformatted `str` |
| `st.columns` | `spec, *, gap, vertical_alignment, border, width, wrap` | `gap` runs from `"xxsmall"` to `"xxlarge"` |
| `st.tabs` | `tabs, *, default, key, on_change, bind` | All tabs compute by default |
| `st.date_input` | `value, min_value, max_value, format, key, bind, persist_state` | Range value returns a tuple of 0-2 dates |
| `st.multiselect` | `options, default, format_func, key, placeholder, persist_state` | Returns a list |
| `st.plotly_chart` | `fig, *, width, height, theme, key, on_select, config` | Use `width="stretch"`; `use_container_width` is deprecated |

## TTL Accepted Values

| Form | Example |
|------|---------|
| Seconds | `ttl=300` |
| Pandas-style string | `ttl="5m"`, `ttl="1h23s"` |
| `timedelta` | `ttl=timedelta(minutes=5)` |
| Disable (`conn.query` only) | `ttl=0` |

## Keeping Widget Values Across Pages

| Option | Works with `pages/` | Use |
|--------|---------------------|-----|
| `persist_state="session"` + same `key` | Yes | Not used here |
| Widgets in the `st.navigation` entrypoint | No | Default for this repo; confirmed across pages |
| Dummy `_key` copied in a callback | Yes | Only if `persist_state` cannot be used |
| `bind="query-params"` | Yes | Shareable filtered URLs |

## Decision Matrix

| Use Case | Choose |
|----------|--------|
| Query result (DataFrame) | `st.cache_data(ttl=...)` |
| SQLAlchemy engine | `st.cache_resource` |
| Dashboard database access | Engine from `src/db.py`, not `st.connection` |
| Quick one-file prototype | `st.connection(...).query(sql, ttl="5m")` |
| Number in a KPI card | Preformatted pt-BR string |
| Slow tabs | `on_change="rerun"` with `if tab.open:` |
| Brand chart colors | `theme.chartCategoricalColors` |

## Common Pitfalls

| Don't | Do |
|-------|-----|
| `@st.cache_data` with no `ttl` on a query | Set an explicit `ttl` |
| SQL strings in `app/pages/` | Keep SQL in `src/queries.py` |
| Import Streamlit in `src/` | Wrap `src/` functions in `app/data.py` |
| Cache a raw psycopg2 connection | Cache a pooled SQLAlchemy engine |
| Set a widget's value after it renders | Change it in a callback |
| Unpack a date range blindly | Check `len(period) == 2` |
| Inline `<svg>` in `st.html` | The sanitizer strips it; use a base64 `<img>` |
| Rely on wheel zoom defaults | Set `scrollZoom: False`, or charts capture page scrolling |
| `format="localized"` for pt-BR | Format in Python; it follows the browser locale |
| Commit `.streamlit/secrets.toml` | Use `.env`; it is ignored by git |
| `streamlit run app/Home.py` with `from src...` | Run from the root with `python -m streamlit run` |

## Related Documentation

| Topic | Path |
|-------|------|
| Multipage layout | `concepts/multipage-apps.md` |
| Cached data layer | `patterns/data-access-layer.md` |
| Sidebar filters | `patterns/sidebar-filters.md` |
| Full Index | `index.md` |
