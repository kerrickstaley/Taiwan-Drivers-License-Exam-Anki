.PHONY: all-apkgs
all-apkgs: apkgs/english-moto-rules-choice.apkg apkgs/english-moto-rules-true.apkg \
		apkgs/english-car-rules-choice.apkg apkgs/english-car-rules-true.apkg \
		apkgs/english-moto-signs-choice.apkg apkgs/english-moto-signs-true.apkg \
		apkgs/english-car-signs-choice.apkg apkgs/english-car-signs-true.apkg

yamls/english-moto-rules-choice.yaml: pdfs/機車法規選擇題-英文1090116.pdf src/generate_yaml_from_pdf.py
	src/generate_yaml_from_pdf.py --input-pdf "$<" --existing-yaml "$@" --output-yaml "$@"

yamls/english-moto-rules-true.yaml: pdfs/機車法規是非題-英文1090116.pdf src/generate_yaml_from_pdf.py
	src/generate_yaml_from_pdf.py --input-pdf "$<" --existing-yaml "$@" --output-yaml "$@"

yamls/english-car-rules-choice.yaml: pdfs/汽車法規選擇題-英文1090116.pdf src/*.py
	src/generate_yaml_from_pdf.py --input-pdf "$<" --existing-yaml "$@" --output-yaml "$@"

yamls/english-car-rules-true.yaml: pdfs/汽車法規是非題-英文1090116.pdf src/*.py
	src/generate_yaml_from_pdf.py --input-pdf "$<" --existing-yaml "$@" --output-yaml "$@"

yamls/english-moto-signs-choice.yaml: pdfs/Signs-Choice／English〈機車標誌選擇題-英文〉.pdf src/*.py
	src/generate_yaml_from_pdf.py --input-pdf "$<" --existing-yaml "$@" --output-yaml "$@" --output-image-dir images

yamls/english-moto-signs-true.yaml: pdfs/Signs-True\ or\ False／English〈機車標誌是非題-英文〉.pdf src/*.py
	src/generate_yaml_from_pdf.py --input-pdf "$<" --existing-yaml "$@" --output-yaml "$@" --output-image-dir images

yamls/english-car-signs-choice.yaml: pdfs/Signs-Choice／English(汽車標誌選擇題-英文).pdf src/*.py
	src/generate_yaml_from_pdf.py --input-pdf "$<" --existing-yaml "$@" --output-yaml "$@" --output-image-dir images

yamls/english-car-signs-true.yaml: pdfs/Signs-True\ or\ False／English(汽車標誌是非題-英文).pdf src/*.py
	src/generate_yaml_from_pdf.py --input-pdf "$<" --existing-yaml "$@" --output-yaml "$@" --output-image-dir images

apkgs/%.apkg: yamls/%.yaml src/*.py
	mkdir -p apkgs
	src/generate_anki_from_yaml.py --input-yamls "$<" --input-image-dir images --output-apkg "$@"

apkgs/all.apkg: yamls/english-moto-rules-choice.yaml yamls/english-moto-rules-true.yaml \
		yamls/english-car-rules-choice.yaml yamls/english-car-rules-true.yaml \
		yamls/english-moto-signs-choice.yaml yamls/english-moto-signs-true.yaml \
		yamls/english-car-signs-choice.yaml yamls/english-car-signs-true.yaml \
		src/*.py
	mkdir -p apkgs
	src/generate_anki_from_yaml.py --input-yamls \
		yamls/english-moto-rules-choice.yaml yamls/english-moto-rules-true.yaml \
		yamls/english-car-rules-choice.yaml yamls/english-car-rules-true.yaml \
		yamls/english-moto-signs-choice.yaml yamls/english-moto-signs-true.yaml \
		yamls/english-car-signs-choice.yaml yamls/english-car-signs-true.yaml \
		--input-image-dir images --output-apkg "$@"
