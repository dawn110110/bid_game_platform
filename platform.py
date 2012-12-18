#! /usr/bin/python

from subprocess import Popen,PIPE
import sys
import os
import random
#classpath variables seprators, and PAUSE function
if os.name =='nt':
	var_sep =';'
	def PAUSE():
		''' on linux or mac , this function is just pass'''
		os.system("PAUSE")
else:
	var_sep =':'
	def PAUSE():
		pass

class AI_Proc(object):
	''' 
	wrapper of ai process
	c / python is ok 
	''' 
	_AI_DIR = ''#'./'

	def __init__(self,filename,lang="c",var=None):
		self.lang = lang
		self.filename = filename
		self.vars = var
		self.result = None

	def run_again(self,var=None):
		''' run this ai again'''
		self.vars = var
		if self.lang in ['c','C','c++','c++','cpp']:
			try:
				self.proc = Popen(self._AI_DIR+self.filename,stdin=PIPE,stdout=PIPE)
			except Exception,e:
				print 'sorry, could not find file %r'%self.filename
				PAUSE()
				sys.exit(0)
				
		elif self.lang in ['py','python','Python','PYTHON']:
			try:
				self.proc = Popen(["python",self._AI_DIR+self.filename],stdin=PIPE,stdout=PIPE)
			except Exception,e:
				print 'sorry, could not find file %r'%self.filename
				
				PAUSE()
				sys.exit(0)
		elif self.lang in ['java','Java','JAVA']:
			try:
				# for java , command is like this "java -cp "C:/axxxx/;AI" Solution"
				# so we have the following ugly codes...
				if self.filename[-6:] =='.class':
					filename=self.filename[:-6] # remove .class
				else:
					filename=self.filename
				# get class name and class path, \\ and / is supported
				if '\\' in filename:
					sep='\\'
				elif '/' in filename:
					sep='/'
				else:
					sep=None
				if sep != None:
					java_class_name = filename.split(sep)[-1]
					java_path = filename[:-len(java_class_name)]
					java_path+=var_sep+"AI/"
				self.proc = Popen(['java','-cp',java_path,java_class_name],stdin=PIPE,stdout=PIPE)
			except Exception,e:
				print '\nSorry, could not find file %r'%self.filename
				PAUSE()
				sys.exit(0)
				
		else:
			print "\nOh! Sorry,%s is not supported.....\nyou can use C/C++/Java/Python to write your code\nHave Fun ^_^\n"%self.lang
			PAUSE()
			sys.exit(0)


	def feed_vars(self):
		''' call this to give variables to ai
		e.g:
		>>>ai.vars = [...]
		>>>ai.feed_vars()
		'''
		if self.vars != None:
			for v in self.vars:
				self.proc.stdin.write(v+'\n')
				self.proc.stdin.flush()
			self.result = self.proc.stdout.read()
			return True
		else:
			return False
	def get_result(self):
		return self.result


class GameLogic(object):
	''' game logic here '''
	def __init__(self,p1,p2):
		''' p1 and p2 are instance of AI_Proc'''
		self.p1 = p1
		self.p2 = p2
		self.reset()
	def reset(self):
		''' reset game varibales'''
		self.scotch_pos = 5
		self.p1_moves = []
		self.p2_moves = []
		self.p2_money = 100
		self.p1_money = 100
		#NOTE: True : first move left. False: first move right
		self.equal_mark = True # bool(random.randint(0,1))

	def win(self,player):
		''' set winner , player is "1" or "2" '''
		player=str(player)
		if player=="1":
			self.winner = self.p1
		elif player =="2":
			self.winner = self.p2
		else:
			raise Exception("wrong varibales: %r"%player)
		self.win_msg = '='*12+"GAME_OVER"+'='*12+"\nwinner is %r (%s)!\np1.moves = %r\np2.moves = %r"%(self.winner.filename,player,self.p1_moves,self.p2_moves)

	def print_log(self):
		print '--------------------------'
		print '\tmove\tmoney\t'
		print 'p1\t%d\t%d'%(self.p1_moves[-1],self.p1_money)
		print 'p2\t%d\t%d'%(self.p2_moves[-1],self.p2_money)
		print 'scotch_pos=%d,'%self.scotch_pos,
		print '-'*self.scotch_pos+"X"+'-'*(10-self.scotch_pos)
	
	def run(self):
		''' do the bid and print logs '''
		print '--------GAME START--------'
		print 'player1 : %s'%self.p1.filename
		print 'player2 : %s'%self.p2.filename

		while True:
			# run ai again
			self.p1.run_again()
			self.p2.run_again()

			self.p1.vars = []
			self.p1.vars = ["1",
					str(self.scotch_pos),
					' '.join([str(x) for x in self.p1_moves]),
					' '.join([str(x) for x in self.p2_moves])
					]
			self.p2.vars = ["2",
					str(self.scotch_pos),
					' '.join([str(x) for x in self.p1_moves]),
					' '.join([str(x) for x in self.p2_moves])
					]

			# feed vars to ai and get result
			self.p1.feed_vars()
			self.p2.feed_vars()

			# get result and remove '\n' at the end
			r1 = self.p1.get_result()

			while True:
				if r1[-1] in ['\n',',','\r','\t']:
					r1=r1[:-1]
				else:
					break
			r2 = self.p2.get_result()

			while True:
				if r2[-1] in ['\n',',','\r','\t']:
					r2=r2[:-1]
				else:
					break
			r1 = int(r1)
			r2 = int(r2)

			# could not more than left money
			if r1>self.p1_money:
				# r1=self.p1_money
				self.win(2)
				break
			if r2>self.p2_money:
				# r2=self.p2_money
				self.win(1)
				break

			# record
			self.p1_moves.append(r1)
			self.p2_moves.append(r2)


			# tell winner
			if r1 <=0:
				self.win(2)
				break
			elif r2<=0:
				self.win(1)
				break

			if r1>r2:
				self.scotch_pos-=1
				self.p1_money-=r1
			elif r1<r2:
				self.scotch_pos+=1
				self.p2_money-=r2
			else:
				if self.equal_mark:
					self.equal_mark=False
					self.scotch_pos-=1
					self.p1_money-=r1
				else:
					self.equal_mark=True
					self.scotch_pos+=1
					self.p2_money-=r2

			# tell winner
			if self.scotch_pos<=0:
				self.win(1)
				break
			elif self.scotch_pos>=10:
				self.win(2)
				break

			# money left
			if self.p1_money<=0:
				self.win(2)
				break
			elif self.p2_money<=0:
				self.win(1)
				break
			# print round result
			self.print_log()
		self.print_log()
		print self.win_msg

if __name__=="__main__":
	import json
	config_words = open("config.json").read()
	configs = json.loads(config_words)

	ai1 = AI_Proc(lang=str(configs[u"player1_lang"]),filename=str(configs[u"player1_file"])) # zhang xin zheng 's ai
	ai2 = AI_Proc(lang=str(configs[u"player2_lang"]),filename=str(configs[u"player2_file"])) # return 10

	game = GameLogic(ai1,ai2)

	game.run() # run the game
	PAUSE()