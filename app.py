#-*- coding: utf-8 -*-
import cfw
import dataLoader as dc
import os
import glob
from flask import Flask, render_template, request, redirect, send_file

# 1. Python console program
class in_console():
	def __init__(self):
		print('='*10, 'Corpus Factory', '='*10)
		print('사용하고 싶은 기능을 선택해주세요.\n1. 엑셀 파일 통합 (txt 파일 생성)\n2. 코퍼스 생성 (yml 파일 생성\n3. 전처리\n4. 종료')
		step1 = input('선택: ')

		if step1 == '1':
			self.uni_excels()
		elif step1 == '2':
			self.raw = dict()
			self.make_corpus()
		else:
			return 0


	def uni_excels(self):
		print('='*10, '엑셀 파일 통합', '='*10)
		print('엑셀 파일이 있는 디렉토리 경로를 입력해주세요.')
		excelpath = input('입력: ')

		while not os.path.isdir(excelpath):
			print('존재하지 않는 디렉토리입니다. 정확한 디렉토리를 다시 입력해주세요. 종료를 위해서는 \'종료\'를 입력해주세요.')
			excelpath = input('입력: ')

			if excelpath == '종료':
				return 0

		print('Q2I 파일을 입력해주세요.')
		q2ipath = input('입력: ')

		while not os.path.isfile(q2ipath):
			print('존재하지 않는 파일입니다. 정확한 위치를 다시 입력해주세요. 종료를 위해서는 \'종료\'를 입력해주세요.')
			q2ipath = input('입력: ')

			if q2ipath == '종료':
				return 0

		dc.make_raw(q2ipath, excelpath)

	def make_corpus(self):
		print('='*10, '코퍼스 생성', '='*10)
		print('corpus raw 파일을 지정해주세요.')
		rawpath = input('입력: ')

		while not os.path.isfile(rawpath):
			print('존재하지 않는 파일입니다. 정확한 위치를 다시 입력해주세요. 종료를 위해서는 \'종료\'를 입력해주세요.')
			rawpath = input('입력: ')

			if rawpath == '종료':
				return 0

		train_ratio = float(input('훈련용 코퍼스의 비율을 지정해주세요 (0 ~ 1): '))

		while not (0 <= train_ratio <= 1):
			print('잘못된 범위를 입력했습니다. 0 ~ 1 사이의 값을 입력해주세요.')


		cfw_obj = cfw.CorpusFactory(rawpath)
		cfw_obj.make_corpus()

# 2. Web application
app = Flask(__name__)

@app.route('/')
def hello():
	return "Hello world!"

@app.route('/cf')
def home():
	return render_template('cf.html')


def file_existance_messages():
	messages = dict()

	if os.path.exists('work/q2i.txt'):
		messages['q2i'] = 'Question to Intention mapping files loaded.'
	else:
		messages['q2i'] = 'No q2i founded. Please upload the q2i file.'

	if os.path.exists('raw.txt'):
		messages['raw'] = 'Raw corpus was maden and loaded. Please upload the contents files.'
	else:
		messages['raw'] = 'No raw corpus founded. Please upload excel files for making raw file.'

	if glob.glob('work/contents/*.txt'):
		messages['cont'] = 'Contents files uploaded.'
	else:
		messages['cont'] = 'No contents files on server. Cannot make yml corpus. Please upload the contents files.'

	return messages

@app.route('/ldfiles')
@app.route('/ldfiles/<filemeth>', methods=['GET', 'POST'])
def excel_load(filemeth=None):
	file_type = request.args.get('type')

	if request.method == 'POST':
		if filemeth == 'xl':
			if file_type == 'q2i':
				file = request.files['q2i']
				file.save(os.getcwd() + '/work/q2i.txt')

				return redirect('/ldfiles/xl')

			elif file_type == 'xl':
				# saving the files for working
				fobj_list = request.files.getlist('xl')
				for fs in fobj_list:
					fs.save(os.getcwd() + '/work/' + fs.filename)

				print('excel files saved in work/ directory.')

				# need q2i file loaded
				if os.path.exists(os.getcwd() + '/work/q2i.txt'):
					dc.make_raw('work/q2i.txt', 'work/')

				return redirect('/ldfiles/xl')

			elif file_type == 'cont':
				fobj_list = request.files.getlist('cont')
				for fs in fobj_list:
					fs.save(os.getcwd() + '/work/contents/' + fs.filename)

				return redirect('/ldfiles/xl')

		elif filemeth == 'raw':
			if file_type == 'raw':
				file = request.files['raw']
				file.save(os.getcwd() + '/raw.txt')

				return redirect('/ldfiles/raw')

			elif file_type == 'cont':
				fobj_list = request.files.getlist('cont')
				for fs in fobj_list:
					fs.save(os.getcwd() + '/work/contents/' + fs.filename)

				return redirect('/ldfiles/raw')

	else:
		messages = file_existance_messages()

		if filemeth == 'xl':
			return render_template('xlfiles.html', q2i_msg=messages['q2i'], raw_msg=messages['raw'], cont_msg=messages['cont'])
		elif filemeth == 'raw':
			return render_template('rawfiles.html', cor_msg=messages['raw'], cont_msg=messages['cont'])
		else:
			return render_template('cf.html')


@app.route('/makeyml', methods=['GET', 'POST'])
def make_yml():
	train_ratio = request.args.get('t_ratio')
	train_ratio = float(train_ratio)

	cps = cfw.CorpusFactory('raw.txt', isEng=False)
	cps.make_corpus(train_ratio)

	for filename in glob.glob('work/*.*'):
		os.remove(filename)
	print('q2i and excel files cleared')

	for filename in glob.glob('work/contents/*.*'):
		os.remove(filename)
	print('contents files cleared')

	os.remove('raw.txt')
	print('raw file cleared')

	return redirect('/download')

@app.route('/train', methods=['GET', 'POST'])
def train_download():
	return send_file('train.yml')
@app.route('/test', methods=['GET', 'POST'])
def test_download():
	return send_file('test.yml')

@app.route('/download', methods=['GET', 'POST'])
def download():
	return render_template('download.html', trainlink='/train', testlink='/test')

@app.route('/reset', methods=['GET', 'POST'])
def reset():
	os.remove('train.yml')
	os.remove('test.yml')
	return redirect('/ldfiles')

@app.route('/pre/<rt>', methods=['POST'])
def preprocessing(rt):
	cps = cfw.CorpusFactory('raw.txt', isEng=False)

	# for English
	if 'tolower' in request.form:
		cps.lower_case()
	if 'toupper' in request.form:
		cps.upper_case()
	if 'stem' in request.form:
		cps.stemming()
	if 'seps' in request.form:
		cps.sep_appo()

	# for public
	if 'num2str' in request.form:
		cps.number_to_string()
	if 'remodup' in request.form:
		cps.remove_dup()
	if 'remospec' in request.form:
		cps.remove_spec()

	# for Korean
	if 'ma' in request.form:
		cps.ma()

	# Special
	if 'tok' in request.form:
		cps.tok2words()

	cps.save()

	return redirect('/ldfiles/{}'.format(rt))


if __name__ == "__main__":
	app.run(host='0.0.0.0', port=3030)