# Schema Evolution & Extensibility

Read this when a feature needs new persisted state, a table keeps growing, or a field is about to be added "just for this release".

## Core principle

Model data by **shape and lifecycle**, not by feature name.

- A **column** is a long-lived schema commitment.
- A **type value** (`ext_type`, `role`, `asset_type`, `plan_type`, `relation_type`, `dimension`, `config_type`) is an extension point.
- Prefer adding a type value over adding a column or a one-off table.

## Classify new data first

| Data shape | Where it belongs | Examples |
| --- | --- | --- |
| Shared state machine | Core table, budgeted | status, stage, progress, fail reason, billing |
| Feature-specific state | Generic extension table | `entity_ext(owner_type, owner_id, ext_type, version, payload_json)` |
| Source/reference media | Generic materials table | `entity_materials(owner_type, owner_id, role, order_no, ...)` |
| Images/audio/cover assets | Generic assets table | `entity_assets(owner_type, owner_id, asset_type, role, uri, meta_json)` |
| Multiple plans/results | Generic plans table | `entity_plans(owner_type, owner_id, plan_type, plan_index, payload_object_path)` |
| Lineage ("where from") | Generic relations table | `entity_relations(from_type, from_id, to_type, to_id, relation_type)` |
| Tag/dimension values | Generic tag relation table | `entity_tags(entity_type, entity_id, dimension, tag_id)` |
| Config snapshots | Generic config table | `entity_configs(owner_id, config_type, version, object_path)` |
| Large AI output/document | Object storage + path | versioned JSON: `{version, model, prompt_version, payload}` |

## Default generic table patterns

```text
*_ext       (owner_type, owner_id, ext_type, version) UNIQUE
            payload_json / payload_object_path
*_materials (owner_type, owner_id, role, order_no) UNIQUE
            typed common fields + ext_json
*_assets    (owner_type, owner_id, asset_type, role, sort)
            uri + meta_json
*_plans     (owner_type, owner_id, plan_type, plan_index) UNIQUE
            payload_object_path + status + ext_json
*_relations (from_type, from_id, to_type, to_id, relation_type) UNIQUE
*_tags      (entity_type, entity_id, dimension, tag_id) UNIQUE
```

Generic does not mean schema-less:

- Keep a unique key over the type tuple.
- Keep a `version` for payload evolution.
- Keep hot fields typed only when they are filtered/sorted/indexed.
- Validate the typed payload in the repository/service layer.

## Rules

1. **Extension-first**: new feature state goes to a generic extension table with a new type value.
2. **Dimensions are rows, not columns**: tags, references, assets, configs, lineage.
3. **One concept, one representation**: do not keep both an object path and an asset ID for the same fact.
4. **Column budget**: warn at ~70 columns on a core table, freeze at ~90; cap additions per release (e.g., 3) unless reviewed.
5. **Promote only hot fields**: a field moves from payload JSON to a typed column only when it is queried/sorted/indexed frequently.
6. **Version AI outputs**: persist `version/model/prompt_version/payload`; structure changes bump version, not schema.
7. **Lineage via relations**: stop adding one `*_source_id` column per feature.
8. **Registry + deprecation**: every column has an owner, status, and removal plan; unused fields are marked deprecated and reviewed quarterly.
9. **Schema snapshot**: generate schema docs from `information_schema`; do not hand-maintain a stale base DDL.
10. **CI gate**: parse migration diffs; fail on too many core-table columns, missing comments/defaults, or generic tables without type keys.

## Migration review — six questions

1. Which lifecycle owns this data: core, feature extension, material, asset, plan, relation, tag, config?
2. Who reads/writes it? Is it used by more than one business line?
3. Can it be a new type value instead of a new column?
4. Does it need an index/sort/filter? If not, why is it a column?
5. What are the default, backfill, and rollback plans?
6. When and how will it be deprecated?

## CI schema gate (cheap version)

- Count `ALTER TABLE <core_table> ADD COLUMN` in the migration diff.
- Fail if > N (e.g., 3) without an explicit "cannot be an extension type" justification.
- Fail on missing `COMMENT` or default.
- Fail on generic tables missing their unique type key or `version`/`payload_json`.
- Fail if the schema snapshot is not regenerated.

## Case study: a rapidly iterated content platform (anonymized)

| Metric | Start | Now |
| --- | --- | --- |
| Tables | 6 | 13 (17 after the redesign) |
| Core task table columns | 47 | 86 (+39, +83%) |
| Analysis table columns | 30 | ~37 |

Of 15 feature iterations, **13 added columns directly to the core task table**. Groups of added columns:

- template metadata: tags, duration, aspect ratio, use/generate counts;
- prompt modes: mode, custom prompt, prompt version;
- references: character refs, audio sequence, style image, reference images, speech ledger;
- lineage: one source-ID column per feature;
- post-processing: process kind/method/source/residual/count, result paths, media metadata;
- recommendation: object path + asset ID.

Root causes:

1. One table mixed template metadata, task instances, pipeline state, post-processing, and billing.
2. Each feature chose the shortest local path — add a column.
3. No default answer for "dimension / lineage / asset / config / output".
4. No column budget, ownership, or migration review.
5. Object storage solved large values but not concept count: one path column per concept.
6. No schema snapshot, deprecation process, or CI diff check.

Fix applied to the redesign:

- Core table: only two template-specific metadata fields.
- Generic extension table: `owner_type + owner_id + ext_type + version + payload_json`.
- Generic materials table: `role + order_no` for source/reference media.
- Generic assets table: `asset_type + role` for scene/transition/cover/audio.
- Generic plans table: `plan_type + plan_index` for multiple plans.
- Later features add type values, not columns or tables.

## Review checklist

- [ ] The new data is classified by shape/lifecycle.
- [ ] A generic table + type value was considered before a new column.
- [ ] Core-table additions are within budget and justified.
- [ ] Hot fields are typed; cold fields stay in versioned JSON.
- [ ] One fact has one representation.
- [ ] Migration has default/backfill/rollback/validation.
- [ ] Column registry and schema snapshot updated.
- [ ] CI schema diff passes.
