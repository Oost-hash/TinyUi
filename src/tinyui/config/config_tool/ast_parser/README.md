# ast_parser

Compileert flat widget configs naar Python dataclasses.

## Gebruik

Alle commands hebben `--templates` / `-t` nodig (pad naar templates directory).

```bash
python -m ast_parser.cli -t <templates_dir> <command>
```

## Commands

### Build

```bash
build -o <output_dir>                  # bouw alle widgets
build -o <output_dir> -w battery       # bouw één widget
build -o <output_dir> -g groupings.json # met groupings
```

### Scan

```bash
scan                        # overzicht cells + columns alle widgets
scan -w battery             # één widget
scan -s 5                   # random sample van 5
scan -w battery -v          # met alle variabelen
```

### Colors

```bash
colors                      # kleur palettes over alle widgets
colors -w battery           # één widget
```

### Prefixes

```bash
prefixes                    # herbruikbare dataclass kandidaten
prefixes -g                 # widget groepen die veel delen
prefixes -m 3 -a 4          # min 3 widgets, min 4 attrs
```

### Suggest

```bash
suggest                     # suggereer dataclasses
suggest -p                  # met Python preview
```

### Rest

```bash
rest                        # wat overblijft na alle patronen
rest -w battery             # voor één widget
```

### Flat

```bash
flat battery                # toon ruwe flat config
flat battery -o out.json    # schrijf naar JSON
```

### Leftover

```bash
leftover                    # sample van 5 widgets na parse + normalize
leftover -w battery         # één widget
leftover -s 10              # sample van 10
leftover-total              # totaal over alle widgets
```

## Output

Alle scan/analyze commands ondersteunen `-o <pad.json>` voor JSON output.
