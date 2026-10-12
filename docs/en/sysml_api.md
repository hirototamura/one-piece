# OMG Systems Modeling API boundary

One-Piece 0.2.0 provides a REST/HTTP read provider for **OMG Systems Modeling API and Services 1.0**. The [formal specification](https://www.omg.org/spec/SystemsModelingAPI/1.0/) defines independent service conformance points. This implementation targets **ProjectService Read** and **ElementNavigationService**. It does not claim conformance to the complete API, OSLC, a SysML language compiler, or a native requirement/parameter metamodel transformation.

## Supported contract

The provider implements these standard operations and paths:

- `getProjects`: `GET /projects`
- `getProjectById`: `GET /projects/{projectId}`
- `getElements`: `GET /projects/{projectId}/commits/{commitId}/elements`
- `getElementById`: `GET /projects/{projectId}/commits/{commitId}/elements/{elementId}`
- `getRootElements`: `GET /projects/{projectId}/commits/{commitId}/roots`
- `getRelationshipsByRelatedElement`: `GET /projects/{projectId}/commits/{commitId}/elements/{relatedElementId}/relationships`

Relationship queries accept `direction=in|out|both`. Collection responses are JSON arrays. They accept `page[size]`, `page[after]` and `page[before]`, and return IETF `Link` headers for `next` and `prev`. The default page size is 100; the maximum is 1,000. Cursors are opaque element or record UUIDs in the selected collection. `excludeUsed=true|false` is accepted. This profile has no ProjectUsages, so that parameter does not change results.

The standard Project, Branch and Commit objects support discovery through `/projects/{projectId}`, `/projects/{projectId}/branches`, `/projects/{projectId}/branches/{branchId}`, `/projects/{projectId}/commits` and `/projects/{projectId}/commits/{commitId}`. Follow `Project.defaultBranch`, then `Branch.head`. These helpers do **not** implement the complete ProjectDataVersioningService Read conformance point. Write operations, query services, tags, diffs, merge and external project usage are outside this release. Unsupported writes return 405 with `Allow: GET`. Errors use the standard `Error` payload and HTTP 400 or 404 as applicable.

The API starts only on an explicit foreground command and binds to loopback. It has no write or baseline operation. It is a local integration boundary, not an authenticated network service.

## Annotation graph profile

The `onepiece-annotation-graph-1` profile uses standard SysML/KerML payload classes:

- One root `Package` identifies the source project.
- Each immutable One-Piece record revision is a `Comment`. Its `body` contains the complete canonical JSON envelope. The body preserves source ID, revision, kind, values, units, uncertainty, approval state, provenance, artifact hashes and references embedded in data. A standard `Annotation` relates that Comment to the project Package.
- Each explicit One-Piece trace edge is a standard `Dependency`. Its `declaredName` is `derive`, `satisfy`, `verify`, `allocate` or `constrain`. `source/client` and `target/supplier` point to the exact source and target record revisions. Edge notes and extension fields remain in the source Comment body.

These five names are **One-Piece relation semantics carried by Dependencies**. They are not native SysML `SatisfyRequirementUsage`, `RequirementVerificationMembership` or `AllocationUsage` instances. In particular, a `verify` Dependency does not assert physical compliance. A receiving tool can navigate and preserve the graph using the standard API before adding a project-specific semantic mapping to native requirement, attribute or part definitions. Arbitrary external SysML models cannot yet be converted into One-Piece requirements automatically.

All annotation graph elements are unowned. Thus `roots` returns all elements with no owner, not just the project Package. No synthetic containment or derived ownership is asserted. No optional FullDerivedProperty or DerivedPropertyPassthrough conformance point is claimed.

UUIDv5 identities include the profile's object category and source project. Record UUIDs include source ID **and revision** so that old and new versions can coexist and exact trace references remain valid. The logical source ID remains in the Comment envelope. A publication Commit UUID includes the complete sorted record digest and profile version. Each provider instance freezes its publication commits at startup. It does not mutate a Commit when the store changes. Restart or export again to publish a new view. Previous export files retain their old commits; the local provider does not serve a repository of previous publication commits. All source record history is retained in each publication.

## Exchange and migration

```sh
onepiece --store projects/balancing-cube/store sysml export /tmp/cube-api.json --project balancing-cube
onepiece --store projects/balancing-cube/store sysml check /tmp/cube-api.json
onepiece --store restored sysml import /tmp/cube-api.json --sha256 EXPECTED_SHA256 --artifacts-root ./verified-artifacts
onepiece --store projects/balancing-cube/store sysml serve --port 9000
```

`export` returns the file SHA-256, Project UUID, Commit UUID and counts. The exchange envelope contains standard `project`, `branch`, `commit` and `elements` payloads, plus the profile identifier and a `commit_request`. The envelope itself is One-Piece's portable format. **Only its `commit_request` value** is the standard POST body for `/projects/{destinationProjectId}/commits` on a compatible external service. Destination project creation, authorization and branch selection remain the responsibility of that service. No remote write is performed by this CLI. Receiving tools may impose additional semantic checks beyond the API schema.

`check` validates the official concrete payload schemas and regenerates the graph from its annotations. It rejects missing elements, changed relationships, UUID drift, inconsistent revisions or a changed CommitRequest. `import` additionally checks the publisher's expected SHA-256, then uses the existing atomic record importer. Existing revisions cannot change. Missing artifact bytes still reject an import; the API export does not carry evidence files. Restore evidence bundles or supply verified artifacts separately. Re-importing an identical exchange remains idempotent. The CLI imports only this lossless annotation profile; it does not treat arbitrary external Comments as approved requirements.

The existing `context`, evidence bundle, HTML and Engineering Agents interfaces remain compatible. No canonical source records are rewritten by this adapter. The published 0.1.1 evidence wheel and its hashes remain unchanged; 0.2.0 is a new package version.

## Official schemas and conformance checks

The installed wheel includes the unchanged official [OpenAPI.json](https://www.omg.org/spec/SystemsModelingAPI/20250201/OpenAPI.json) and [Schema.json](https://www.omg.org/spec/SystemsModelingAPI/20250201/Schema.json), with their URLs, retrieval date, byte sizes and SHA-256 values in [sources.json](../../src/onepiece/standards/omg/SystemsModelingAPI/1.0/sources.json). Both files are verified before use. These OMG documents retain their original ownership; the repository's Apache license does not relicense them.

Validation uses the OpenAPI response and request components. For offline resolution, the validator embeds Schema Objects under one document, removes their resource `$id` values, and resolves known relative/absolute component references to their packaged component names. It changes no field constraints. The original files remain byte-for-byte unchanged. Concrete response validation selects the actual metaclass branch of each official inheritance union. Tests also validate the complete standard CommitRequest schema, not a custom substitute.

`tests/test_sysml_api.py` exercises the applicable tests from the [specification's Annex A](https://www.omg.org/spec/SystemsModelingAPI/1.0/PDF):

- A.1, PIM-PS-002 through PIM-PS-004: list, retrieve and absent project.
- A.2, PIM-EN-001 through PIM-EN-005: list and retrieve elements, absent element, incoming and outgoing relationships.
- A.7, PIM-CC-001 through PIM-CC-005 and PIM-CC-007: required inputs, unknown projects/commits, commit from another project, and required UUID.
- The additional root operation, standard REST paths, discovery, forward/back pagination, errors, invalid direction, write denial, immutable snapshots, exact revision targets, schema formats and lossless exchange are tested directly.

PIM-CC-006 concerns creation with a missing name and does not apply to this read provider. Tests are local self-checks of the selected conformance points. An independent OMG certification or a round trip through a third-party repository has not been performed.
