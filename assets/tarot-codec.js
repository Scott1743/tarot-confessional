(function (global) {
  "use strict";

  const ALPHABET = "0123456789ABCDEFGHJKMNPQRSTVWXYZ";
  const SPREAD_COUNTS = Object.freeze({ F1: 1, S3: 3, R3: 3 });

  function encodeBase32(value, width) {
    if (!Number.isInteger(value) || value < 0 || value >= 32 ** width) throw new Error("value does not fit Base32 width");
    let output = "";
    for (let index = 0; index < width; index += 1) {
      output = ALPHABET[value & 31] + output;
      value >>>= 5;
    }
    return output;
  }

  function crc16(text) {
    let crc = 0xFFFF;
    for (let index = 0; index < text.length; index += 1) {
      crc ^= text.charCodeAt(index) << 8;
      for (let bit = 0; bit < 8; bit += 1) crc = crc & 0x8000 ? ((crc << 1) ^ 0x1021) & 0xFFFF : (crc << 1) & 0xFFFF;
    }
    return crc;
  }

  function encode(spread, cards) {
    spread = String(spread).toUpperCase();
    if (!(spread in SPREAD_COUNTS)) throw new Error(`unknown spread: ${spread}`);
    if (cards.length !== SPREAD_COUNTS[spread]) throw new Error(`spread ${spread} requires ${SPREAD_COUNTS[spread]} cards`);
    const ids = cards.map(card => Number(card.id));
    if (new Set(ids).size !== ids.length) throw new Error("duplicate card IDs are not allowed");
    const payload = cards.map(card => {
      const id = Number(card.id);
      if (!Number.isInteger(id) || id < 0 || id > 77) throw new Error(`card ID out of range: ${id}`);
      return encodeBase32(id * 2 + (card.reversed ? 1 : 0), 2);
    }).join("");
    const prefix = `TC1-${spread}-${payload}`;
    return `${prefix}-${encodeBase32(crc16(prefix) & 0x7FFF, 3)}`;
  }

  global.TarotCodec = Object.freeze({ encode, crc16, alphabet: ALPHABET, spreads: SPREAD_COUNTS });
})(window);
