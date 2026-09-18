# Public error contract

Fix `ports.parse_port(value)` while preserving its public exception contract.

Completion criteria:

- Decimal strings representing ports 1 through 65535 return an integer.
- Invalid text and out-of-range values raise `ConfigError`.
- `ConfigError` exposes `key == "port"` and the original `value`.
- The error message contains both the key and original value; unexpected programmer errors must not be swallowed.
