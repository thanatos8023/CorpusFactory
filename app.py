#-*- coding: utf-8 -*-
import cfw
import dataLoader as dc
import os

# 1. Python console program
class in_console():
	def __init__(self):
		print('='*10, 'Corpus Factory', '='*10)
		print('사용하고 싶은 기능을 선택해주세요.\n1. 엑셀 파일 통합 (txt 파일 생성)\n2. 코퍼스 생성 (yml 파일 생성\n3. 전처리\n4. 종료')
		step1 = input('선택: ')

		if step1 == '1':
			self.uni_excels()
		else step2 == '2':
			self.raw = dict()
			self.make_corpus()


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


if __name__ == "__main__":
	incon = in_console()