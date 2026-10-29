## Results and Verification

### CI measurements

| Run | Trigger | Total CI duration |
|---|---|---|
| CI #5 | Pull request | 206 seconds |
| CI #6 | Push to main | 181 seconds |
| CI #7 | Manual workflow run | 143 seconds |

The total CI duration decreased by 63 seconds (30.6%) between CI #5 and CI #7.

### Cache verification

GitHub Actions successfully imported and exported Buildx cache using the GitHub Actions cache backend.

During CI #7, six Docker build steps were confirmed as `CACHED`, including:

- `RUN pip install --no-cache-dir uv`
- `COPY pyproject.toml uv.lock ./`
- `COPY src/ ./src/`
- `RUN uv sync --locked --no-dev --no-editable`
- `COPY data/ ./data/`

The most significant result was that `uv sync --locked` was restored from cache instead of reinstalling the Python dependencies.

### Analysis

The implementation demonstrates that Docker Buildx can reuse unchanged image layers across GitHub Actions runs.

The recorded total workflow duration decreased from 206 to 143 seconds across three runs. This is consistent with improved cache reuse, although other factors such as runner performance, network conditions and workflow execution differences may also have contributed.

All three measurements were collected after the Buildx implementation. Therefore, they demonstrate changes between cached workflow runs rather than a controlled comparison against the original build method.

### Trade-offs

- Persistent cache requires additional cache storage.
- Importing and exporting cache adds overhead.
- In an earlier run, cache export alone required 31.2 seconds.
- Changes to source code, dependencies or model artifacts may invalidate affected build layers.
- Cache reuse must not bypass model verification or automated smoke-testing.

### Conclusion

Docker Buildx caching was successfully implemented and verified. CI #7 reused six Docker build steps, including the dependency installation layer.

The repeated workflow runs also showed a reduction in total CI duration, from 206 seconds to 143 seconds.

The results confirm functioning cache reuse, while the exact performance improvement compared with the original uncached Docker build remains unquantified.