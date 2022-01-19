
# Kaldi Data Preparation
Tool to transform data from Nemo/Deepspeech format to Kaldi as described here — https://kaldi-asr.org/doc/data_prep.html

## Requirements
python >= 3.5

**[Kenlm](https://github.com/kpu/kenlm)** (for building LM)

## Usage
```
git clone https://github.com/samespace/kaldi-data-preperation.git && cd kaldi-data-preperation
pip3 install -r requirements.txt

python3 data.py -h
```

## Example
```
python3 data.py dicts/dict-en.ipa data.csv
```

## License
Read **[LICENSE](LICENSE)** 

This repo is licensed under **[GNU GPL V3](https://www.gnu.org/licenses/gpl-3.0.en.html)** license
