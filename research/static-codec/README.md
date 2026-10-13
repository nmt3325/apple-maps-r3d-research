# Static codec evidence

`codec-arm64.b64` contains 118,784 inert bytes from the existing VectorKit analysis file, VM interval `0x1b7095000..0x1b70b2000`. `capture.json` records the range and SHA-256. These bytes were read as data; no Apple code was executed. The independent Python decoder does not read them.

`decompiled/` is Ghidra pseudocode, not executable C and not the independent decoder. Missing external targets and SIMD type reconstruction cause warnings and misleading variable types in some functions. Check decisive operations against the captured ARM64 instructions and full array audits. In particular, the quantized sentinel dispatch is at `0x1b70b001c..0x1b70b0038`, UV reciprocal normalization at `0x1b70a8f4c..0x1b70a8f70`, and material truncation at `0x1b70aec20..0x1b70aec30`.

To regenerate on Linux, decode the Base64 to a temporary binary, then run Ghidra's `analyzeHeadless` with `AARCH64:LE:64:v8A`, `BinaryLoader`, base address `0x1b7095000`, and the supplied `DecompileCodec.java` post-script. Java 21 and Ghidra 12.1.4 were used. These research dependencies are unnecessary for running or validating the independent decoder.
