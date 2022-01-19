
# Kaldi Data Preparation

Python tool to convert data from Nemo/Deepspeech format to Kaldi format described in https://kaldi-asr.org/doc/data_prep.html

## Requirements
python >= 3.5
**[Kenlm](https://github.com/kpu/kenlm)** (for building LM)

## Usage
```
git clone https://github.com/splunk/pion.git && cd pion
pip3 install -r requirements.txt

python3 data.py <>
```

## Example
```
cd example

./run.sh
```

## License
This repo is licensed under **[GNU GPL V3](https://www.gnu.org/licenses/gpl-3.0.en.html)** license