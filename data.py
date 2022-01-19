import sys
import logging
import os
import csv
import shutil

from optparse       import OptionParser
from phonetics      import ipa2xsampa
from lexicon         import Lexicon


def read_all_transcripts(csv_file):
    ts_all = []
    with open(csv_file, newline='') as csvfile:
        csvreader = csv.reader(csvfile)
        for row in csvreader:
            ts_all.append((os.path.basename(row[0]),row[0],row[1]))
    return ts_all


def split_train_data(ts, split=0.2):
    from sklearn.model_selection import train_test_split
    train, test = train_test_split(ts, test_size=split)
    return train, test


def convert_list_to_map(ts_list):
    ts_map = {}
    for l in ts_list:
        ts_map[l[0]] = (l[1], l[2])
    return ts_map

def is_tool(name):
    """Check whether `name` is on PATH and marked as executable."""

    # from whichcraft import which
    from shutil import which

    return which(name) is not None

def export_kaldi_data (destdirfn, tsdict):
    logging.info ( "Exporting kaldi data to %s..." % destdirfn)

    os.makedirs(destdirfn)

    with open(destdirfn+'wav.scp','w') as wavscpf,  \
         open(destdirfn+'utt2spk','w') as utt2spkf, \
         open(destdirfn+'text','w') as textf:

        for utt_id in sorted(tsdict):
            pth, ts = tsdict[utt_id]

            textf.write(u'%s %s\n' % (utt_id, ts))

            wavscpf.write('%s %s\n' % (utt_id, pth))

            utt2spkf.write('%s %s\n' % (utt_id, utt_id))


def export_dictionary(ts_all, lex, dictfn2):
    logging.info("Exporting dictionary...")
    utt_dict = {}
    for token in lex:
        utt_dict[token] = lex.get_multi(token)

    ps = {}
    with open(dictfn2, 'w') as dictf:

        dictf.write('!SIL SIL\n')

        for token in sorted(utt_dict):
            for form in utt_dict[token]:
                ipa = utt_dict[token][form]['ipa']
                xsr = ipa2xsampa(token, ipa, spaces=True)

                xs = (xsr.replace('-', '')
                         .replace('\' ', '\'')
                         .replace('  ', ' ')
                         .replace('#', 'nC'))

                dictf.write(('%s %s\n' % (token, xs)))

                for p in xs.split(' '):

                    if len(p) < 1:
                        logging.error(
                            u"****ERROR: empty phoneme in : '%s' ('%s', ipa: '%s', token: '%s')" % (
                            xs, xsr, ipa, token))

                    pws = p[1:] if p[0] == '\'' else p

                    if not pws in ps:
                        ps[pws] = {p}
                    else:
                        ps[pws].add(p)
    logging.info("%s written." % dictfn2)
    logging.info("Exporting dictionary ... done.")

    return ps, utt_dict


def write_nonsilence_phones(ps, psfn):
    with open(psfn, 'w') as psf:
        for pws in ps:
            for p in sorted(list(ps[pws])):
                psf.write(('%s ' % p))

            psf.write('\n')
    logging.info('%s written.' % psfn)


def write_silence_phones(psfn):
    with open(psfn, 'w') as psf:
        psf.write('SIL\nSPN\nNSN\n')
    logging.info('%s written.' % psfn)


def write_optional_silence(psfn):
    with open(psfn, 'w') as psf:
        psf.write('SIL\n')
    logging.info('%s written.' % psfn)


def write_extra_questions(ps, psfn):
    with open(psfn, 'w') as psf:
        psf.write('SIL SPN NSN\n')

        for pws in ps:
            for p in ps[pws]:
                if '\'' in p:
                    continue
                psf.write(('%s ' % p))
        psf.write('\n')

        for pws in ps:
            for p in ps[pws]:
                if not '\'' in p:
                    continue
                psf.write(('%s ' % p))

        psf.write('\n')
    logging.info('%s written.' % psfn)


def create_training_data_for_language_model(utt_dict, data_dir, transcripts):
    os.makedirs('%s/lm' % data_dir)
    text_fn = '%s/lm/train_nounk.txt' % data_dir
    with open(text_fn, 'w') as f:
        for utt_id in sorted(transcripts):
            pth, ts = transcripts[utt_id]
            f.write(('%s\n' % ts))
    logging.info("%s written." % text_fn)
    fn = '%s/lm/wordlist.txt' % data_dir
    with open(fn, 'w') as f:
        for token in sorted(utt_dict):
            f.write(('%s\n' % token))
    logging.info("%s written." % fn)
    if is_tool("lmplz") is False:
        logging.info("lmplz is not installed or is not on PATH.")
        quit()
    lm_fn = '%s/lm/lm.arpa' % data_dir
    cmd = 'lmplz -S 50%% --text %s --arpa %s --order 3' % (text_fn , lm_fn)
    os.system(cmd)
    logging.info("%s written." % lm_fn)
    lm_gz = '%s/lm/lm.gz' % data_dir
    cmd = 'gzip -c %s > %s' % (lm_fn, lm_gz)
    os.system(cmd)
    logging.info("%s written." % lm_gz)

#
# commandline
#

parser = OptionParser("usage: %prog [options] <dict> <csv_path>")

parser.add_option ("-d", "--debug", dest="debug", type='int', default=0, help="Limit number of sentences (debug purposes only), default: 0")

parser.add_option ("--test_split", dest="test_split", type='float', default=0.2, help="ratio of test to train split")

parser.add_option ("-v", "--verbose", action="store_true", dest="verbose", help="verbose output")

(options, args) = parser.parse_args()

if options.verbose:
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO)

dictionary     = args[0]
csv_file       = args[1]

data_dir = 'data'

if os.path.isdir(data_dir):
    shutil.rmtree(data_dir)

#
# generate speech and text corpora
#

ts_list = read_all_transcripts(csv_file)
train_ts_list, test_ts_list = split_train_data(ts_list, options.test_split)

ts_all = convert_list_to_map(ts_list)
ts_train = convert_list_to_map(train_ts_list)
ts_test = convert_list_to_map(test_ts_list)

logging.info("loading transcripts done, total: %d train, %d test samples." % (len(ts_train), len(ts_test)))

export_kaldi_data('%s/train/' % data_dir, ts_train)
export_kaldi_data('%s/test/' % data_dir, ts_test)

#
# export dict
#

os.makedirs('%s/dict' % data_dir)
ps, utt_dict = export_dictionary(ts_all, Lexicon(file_path=dictionary), '%s/dict/lexicon.txt' % data_dir)
write_nonsilence_phones(ps, '%s/dict/nonsilence_phones.txt' % data_dir)
write_silence_phones('%s/dict/silence_phones.txt' % data_dir)
write_optional_silence('%s/dict/optional_silence.txt' % data_dir)
write_extra_questions(ps, '%s/dict/extra_questions.txt' % data_dir)
create_training_data_for_language_model(utt_dict, data_dir, ts_all)
logging.info ( "All done." )