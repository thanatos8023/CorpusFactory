#-*- coding: utf-8 -*-
import mecab
import dataLoader as dc
import inflect
import re
import nltk
from collections import Counter
import os
import random

class CorpusFactory ():
	def __init__(self, rawpath, isEng=False):
		self.isEng = isEng

		# inflect engine: number_to_string(int)
		self.p = inflect.engine()

		# mecab class
		self.meCab = mecab.MeCab()

		# Loading raw corpus file
		self.raw = dc.load_raw(rawpath)

		self.contents = self.load_contents('work/contents/')

	def save(self):
		with open('raw.txt', 'w', encoding='utf-8') as f:
			for intention in self.raw:
				for sent in self.raw[intention]:
					f.write('%s\t%s\n' % (sent, intention))

	# Converting number to korean
	def __read_number_kor__(self, matchednum):
		n2kmap = ['영', '일', '이', '삼', '사', '오', '육', '칠', '팔', '구']

		num = int(matchednum.group())
		num_str = ''

		if num < 0:
			num_str = "영하 "
			num = num * -1

		num_list = list()

		while num:
			res = num % 10
			num_list.append(res)
			num = num // 10

		# num_list: Reversal number list of interger
		# one
		if len(num_list) == 1:
			num_str = n2kmap[num]
		elif len(num_list) == 2:
			if num_list[1] == 1:
				num_str = num_str + "십 " + n2kmap[num_list[0]]
			else:
				num_str = num_str + n2kmap[num_list[1]] + " 십 " + n2kmap[num_list[0]]
		elif len(num_list) == 3:
			if num_list[2] == 1:
				num_str = num_str + '백 ' + n2kmap[num_list[1]] + " 십 " + n2kmap[num_list[0]]
			else:
				num_str = num_str + n2kmap[num_list[2]] + ' 백 ' + n2kmap[num_list[1]] + " 십 " + n2kmap[num_list[0]]
		elif len(num_list) == 4:
			if num_list[3] == 1:
				num_str = num_str + '천 ' + n2kmap[num_list[2]] + ' 백 ' + n2kmap[num_list[1]] + " 십 " + n2kmap[num_list[0]]
			else:
				num_str = num_str + n2kmap[num_list[3]] + ' 천 ' + n2kmap[num_list[2]] + ' 백 ' + n2kmap[num_list[1]] + " 십 " + n2kmap[num_list[0]]
		else:
			num_str = ''

		return num_str

	# Converting number to string (english)
	def __read_number_eng__(self, num):
		return self.p.number_to_words(num)

	# corpus handle
	def number_to_string(self):
		print('Preprocessing :: Converting numbers to string')
		for key in self.raw.keys():
			for i in range(len(self.raw[key])):
				if self.isEng:
					self.raw[key][i] = re.sub(r'-?[0-9]+', self.__read_number_eng__, self.raw[key][i])
				else:
					self.raw[key][i] = re.sub(r'-?[0-9]+', self.__read_number_kor__, self.raw[key][i])
		return self.raw

	# Remove duplication
	def remove_dup(self):
		print('Preprocessing :: Remove duplication')
		for key in self.raw.keys():
			self.raw[key] = list(set(self.raw[key]))

		return self.raw

	# Remove special chractor
	# Remain '
	def remove_spec(self):
		print('Preprocessing :: Remove special character')
		for key in self.raw.keys():
			for i in range(len(self.raw[key])):
				self.raw[key][i] = re.sub(r'[^0-9가-힣A-Za-z\s\'<>]', '', self.raw[key][i])
		return self.raw

	def tok2words(self, need_count=False):
		print('Preprocessing :: Tokenize to word list')
		tokens = list()
		for key in self.raw.keys():
			for sent in self.raw[key]:
				tokens += nltk.word_tokenize(sent)

		if need_count:
			result = list()
			c = Counter(tokens)
			for key in c.keys():
				result.append((key, c[key]))
		else:
			result = list(set(tokens))

		with open(os.getcwd()+'/tokens.txt', 'w', encoding='utf-8') as f:
			for word in result:
				f.write(word)
				f.write('\n')

		print('Result: tokens.txt saved in', os.getcwd())

		return result

	# Morpheme analyzer except <> tag
	def __analyzer__(self, sentence, tag=True):
		if tag:
			sent_full = self.meCab.pos(sentence)
			result = ''
			for mph, tag in sent_full:
				result += '%s/%s ' % (mph, tag)
			result = re.sub('</SY ([A-Z]+)/SL >/SY', lambda m: '<' + m.group(1) + '>', result)
		else:
			sent_full = self.meCab.morphs(sentence)
			result = ''
			for mph, tag in sent_full:
				result += '%s ' % mph
			result = re.sub('< ([A-Z]+) >', lambda m: '<' + m.group(1) + '>', result)
		return result.strip()

	# Process morpheme analyze
	def ma(self, tag=True):
		print('Preprocessing :: Morpheme analyzer')
		for key in self.raw.keys():
			for i in range(len(self.raw[key])):
				self.raw[key][i] = self.__analyzer__(self.raw[key][i], tag)
		return self.raw

	# Change to lower case
	def lower_case(self):
		print('Preprocessing :: Convert to lowercase')
		for key in self.raw.keys():
			for i in range(len(self.raw[key])):
				self.raw[key][i] = re.sub(r'[A-Z]', lambda m: m.group(0).lower(), self.raw[key][i])
		return self.raw

	# Change to upper case
	def upper_case(self):
		print('Preprocessing :: Convert to uppercase')
		for key in self.raw.keys():
			for i in range(len(self.raw[key])):
				self.raw[key][i] = re.sub(r'[a-z]', lambda m: m.group(0).upper(), self.raw[key][i])
		return self.raw

	# Stemming
	def stemming(self):
		print('Preprocessing :: Stemming')
		ps = nltk.stem.PorterStemmer()
		for key in self.raw.keys():
			for i in range(len(self.raw[key])):
				tok = nltk.word_tokenize(self.raw[key][i])
				for j in range(len(tok)):
					tok[j] = ps.stem(tok[j])
				self.raw[key][i] = ' '.join(tok)
		return self.raw

	# Seperating 's
	def sep_appo(self):
		print('Preprocessing :: Seperating \'s')
		for key in self.raw.keys():
			for i in range(len(self.raw[key])):
				self.raw[key][i] = re.sub("([a-zA-Z])('[a-z])\s?", lambda m: '%s %s ' % (m.group(1), m.group(2)), self.raw[key][i])
		return self.raw

	# Slot filling the single sentence from contents file
	def load_contents(self, contents_path):
		contents = dict()

		for fpath in os.listdir(contents_path):
			conname = os.path.basename(fpath).replace('.txt', '')
			with open(os.path.abspath(contents_path+fpath), 'rb') as f:
				data = f.read()
				try:
					data = data.decode('utf-8')
				except UnicodeDecodeError:
					data = data.decode('euc-kr')
				conlist = data.split('\n')
			contents[conname] = conlist

		for key in contents.keys():
			for i in range(len(contents[key])):
				contents[key][i] = contents[key][i].replace('\ufeff', '')

		return contents

	def __fill_slot__(self, sentence):
		slot_re = re.compile('<[A-Z]+>')
		for slot in slot_re.findall(sentence):
			slotname = slot[1:len(slot)-1]
			sentence = sentence.replace(slot, random.choice(self.contents[slotname]))
		return sentence

	# making corpus
	# necessary: raw corpus object, contents object, saving path, traning corpus ratio)

	# corpus form :
	#- goal: ac_on
	#  utterance: 에어컨/NNG 바람/NNG 나와/VV+EC 봐/VX+EC

	def preprocessing(self):
		# uniform preprocessing
		self.number_to_string()
		self.remove_dup()
		self.remove_spec()
		self.ma()

	def make_corpus(self, train_ratio):
		self.preprocessing()

		train_form = ''
		test_form = ''

		for key in self.raw.keys():
			train_idx = round(len(self.raw[key]) * train_ratio)
			for i in range(train_idx):
				train_form += '- goal: %s\n  utterance: %s\n' % (key, self.raw[key][i])
			for j in range(train_idx, len(self.raw[key])):
				test_form += '- goal: %s\n  utterance: %s\n' % (key, self.raw[key][j])

		with open(os.getcwd()+'/train.yml', 'w', encoding='utf-8') as f:
			f.write(train_form)
			print('Result: train.yml saved in', os.getcwd())
		with open(os.getcwd()+'/test.yml', 'w', encoding='utf-8') as f:
			f.write(test_form)
			print('Result: test.yml saved in', os.getcwd())