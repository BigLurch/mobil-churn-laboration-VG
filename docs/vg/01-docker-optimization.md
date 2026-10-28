# VG 1 – Docker Security and Image Optimization

## Objective

Improve the security and resource efficiency of the existing Docker image while preserving the churn prediction functionality.

## Baseline measurements

| Metric | Before |
|---|---|
| Build time (no cache) | 140 s |
| Image size | 252,662,433 bytes |
| Container user | root (UID 0) |
| Smoke-test | PASS |

## Improvement 1 – Non-root execution

### Problem

The original container executed the application as root (UID 0), providing more privileges than necessary.

### Implementation

Created a dedicated non-root user with UID 10001 and configured the Dockerfile to run the application under that user.

Adjusted ownership of the output directory to allow the application to generate its call list without root privileges.

### Results

| Metric | Before | After |
|---|---|---|
| Build time | 140 s | 109 s |
| Image size | 252,662,433 bytes | 252,662,989 bytes |
| Container UID | 0 | 10001 |
| Smoke-test | PASS | PASS |

### Analysis

The container now runs without root privileges, reducing the application's permissions while preserving functionality.

The image size increased by only 556 bytes. The measured build time decreased by 31 seconds, but a single build per version is insufficient to establish that the code change caused the difference.

### Trade-offs

The solution requires explicit directory ownership and permission management. Future changes to output directories may require corresponding Dockerfile updates.

## Improvement 2 – Multi-stage Docker build

*To be implemented and measured.*

## Conclusion

*To be completed after both changes have been verified.*

## Pull Request

*Link to be added after PR creation.*