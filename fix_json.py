with open("datos_stock.json", "r", encoding="windows-1252") as f:  # reemplazá con la codificación correcta
    data = f.read()

with open("datos_stock_fixed.json", "w", encoding="utf-8") as f:
    f.write(data)

print("Archivo convertido a UTF-8 sin BOM: datos_stock_fixed.json")