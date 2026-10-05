# RFC 3161 timestamp notice

The English freeze protocol was timestamped before any confirmatory outcome inspection. This notice exposes the verification anchors without including local credential material.

- Protocol file: `RRC-ACT_preregistration_freeze_v1.1.md`
- Protocol SHA-256: `da6aa7119efbe9c602157791e8f5b5c00a92a2a7f5d42d193dce5d9c662c2165`
- FreeTSA token: `timestamp/freetsa.tsr`
- FreeTSA time: `2026-10-05 08:49:49 UTC`
- DigiCert token: `timestamp/digicert.tsr`
- DigiCert time: `2026-10-05 08:49:50 UTC`

Verify against this repository checkout:

```sh
openssl ts -verify -data RRC-ACT_preregistration_freeze_v1.1.md \
  -in timestamp/freetsa.tsr -CAfile /path/to/freetsa_cacert.pem
openssl ts -verify -data RRC-ACT_preregistration_freeze_v1.1.md \
  -in timestamp/digicert.tsr -CAfile /etc/ssl/cert.pem
```

On this machine, `/path/to/freetsa_cacert.pem` is `/Users/yuanjinggongsheng/agent_memory/tools/freetsa_cacert.pem`; use the TSA's published CA bundle on another machine. Both commands report `Verification: OK` here. The timestamp proves the hash of the protocol existed at the TSA times; it does not mean the protocol has been registered on OSF/AsPredicted or that the experiment has been run.
