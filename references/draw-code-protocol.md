# TC1 Draw Code Protocol

`TC1` is the stable transport format between the offline draw page and the host Agent.

## Format

```text
TC1-<SPREAD>-<PAYLOAD>-<CHECKSUM>
```

Example:

```text
TC1-S3-023N15-6KQ
```

## Alphabet

Use Crockford Base32 without ambiguous characters:

```text
0123456789ABCDEFGHJKMNPQRSTVWXYZ
```

Decoders accept lowercase and normalize `O -> 0`, `I/L -> 1`.

## Card token

Each selected card occupies exactly two Base32 characters.

```text
value = card_id * 2 + orientation_bit
orientation_bit = 0 upright, 1 reversed
```

Valid card IDs are `0..77`, so valid encoded values are `0..155`.

## Spreads

| ID | Card count | Positions |
|---|---:|---|
| `F1` | 1 | focus |
| `S3` | 3 | situation, friction, direction |
| `R3` | 3 | self, other, relationship |

The payload length must equal `card_count * 2`. Duplicate card IDs are invalid.

## Checksum

1. Build the ASCII prefix `TC1-<SPREAD>-<PAYLOAD>`.
2. Calculate CRC-16/CCITT-FALSE with polynomial `0x1021` and initial value `0xFFFF`.
3. Keep the low 15 bits with `crc & 0x7FFF`.
4. Encode the result as exactly three Crockford Base32 characters.

The checksum detects copying mistakes. It is not encryption, authentication, or anti-cheat protection.

## Privacy

The code contains only protocol version, spread, ordered card IDs, orientations, and checksum. It never contains the user's question, timestamp, identity, or device data.
