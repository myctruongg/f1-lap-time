// Illustrative scenario inputs for the frontend demo.
export const tracks = {
  bahrain: {
    name: "Bahrain International Circuit", location: "Sakhir, Bahrain",
    profile: "Mixed layout", corners: 15, length: 5.412,
    baseSeconds: 95.2, cornerShare: 0.52,
    outline: [[241, 166], [71, 154], [49, 142], [56, 129], [48, 114], [59, 99],
      [147, 77], [161, 64], [158, 53], [144, 48], [161, 36], [191, 39],
      [211, 48], [205, 65], [219, 77], [211, 91], [174, 102], [183, 115],
      [245, 122], [260, 139], [258, 151]],
  },
  monza: {
    name: "Autodromo Nazionale Monza", location: "Monza, Italy",
    profile: "Straight-heavy layout", corners: 11, length: 5.793,
    baseSeconds: 82.5, cornerShare: 0.28,
    outline: [[245, 158], [81, 161], [69, 149], [75, 140], [63, 130], [38, 133],
      [27, 123], [38, 105], [74, 85], [104, 77], [110, 65], [122, 65],
      [129, 51], [146, 43], [164, 47], [178, 38], [198, 43], [201, 61],
      [192, 110], [204, 116], [202, 128], [213, 134], [263, 136], [272, 145]],
  },
  monaco: {
    name: "Circuit de Monaco", location: "Monte Carlo, Monaco",
    profile: "Corner-heavy layout", corners: 19, length: 3.337,
    baseSeconds: 76.8, cornerShare: 0.78,
    outline: [[130, 158], [184, 155], [198, 139], [237, 126], [251, 111],
      [259, 91], [247, 70], [233, 74], [219, 63], [211, 43], [198, 37],
      [190, 49], [196, 62], [183, 70], [155, 50], [139, 49], [103, 62],
      [83, 79], [91, 90], [120, 96], [146, 107], [136, 117], [108, 111],
      [91, 121], [68, 114], [53, 125], [34, 125], [29, 140], [42, 149],
      [61, 146], [75, 156], [96, 148]],
  },
};

export const drivers = {
  verstappen: { name: "Max Verstappen", offset: 0 },
  norris: { name: "Lando Norris", offset: 0.18 },
  leclerc: { name: "Charles Leclerc", offset: 0.24 },
  hamilton: { name: "Lewis Hamilton", offset: 0.36 },
  piastri: { name: "Oscar Piastri", offset: 0.28 },
  russell: { name: "George Russell", offset: 0.33 },
};

export const weather = {
  dry: { name: "Dry", symbol: "☀", penalty: 0 },
  damp: { name: "Damp", symbol: "☁", penalty: 0.055 },
  wet: { name: "Wet", symbol: "☂", penalty: 0.125 },
};

export function predictLap({ track, driver, condition }) {
  const circuit = tracks[track];
  const dryTime = circuit.baseSeconds + drivers[driver].offset;
  const weatherPenalty = weather[condition].penalty * (0.8 + circuit.cornerShare * 0.55);
  return dryTime * (1 + weatherPenalty);
}

export function formatLap(seconds) {
  const milliseconds = Math.round(seconds * 1000);
  const minutes = Math.floor(milliseconds / 60_000);
  return `${minutes}:${((milliseconds % 60_000) / 1000).toFixed(3).padStart(6, "0")}`;
}
