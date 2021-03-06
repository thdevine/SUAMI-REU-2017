'''
from pandas_datareader import data as web
from selenium import webdriver
import time

#Scraping Portion of algo
num_options = int( input("How many options do you want to iterate over? ") )
date = input("Enter the last trading day (y-m-d): ")

#filepath removed
chrome_path = "..............."
driver  = webdriver.Chrome(chrome_path)
driver.get("https://finance.yahoo.com/quote/AAPL/options/")
time.sleep(2)
driver.find_element_by_xpath("""//*[@id="quote-leaf-comp"]/section/div/div[1]/select/option[5]""").click() #selects exp date July 21, 2017
time.sleep(2)
#This is not a mistake. We want the volumes to be sorted from top to bottom, so 'volume' has to be clicked on twice
driver.find_element_by_xpath("""//*[@id="quote-leaf-comp"]/section/section[2]/div[2]/table/thead/tr/th[8]/span""").click()
time.sleep(1)
driver.find_element_by_xpath("""//*[@id="quote-leaf-comp"]/section/section[2]/div[2]/table/thead/tr/th[8]/span""").click()

#####
# Get options we want
strike_last_list = []
index = 1
while index <= num_options:

        strike = driver.find_element_by_xpath("""//*[@id="quote-leaf-comp"]/section/section[2]/div[2]/table/tbody/tr[""" + str(index) + """]/td[1]/a""")
        last   = driver.find_element_by_xpath("""//*[@id="quote-leaf-comp"]/section/section[2]/div[2]/table/tbody/tr[""" + str(index) + """]/td[3]""")

        strike_last_list.append( [strike.text, last.text] )

        index += 1

#for printing purposes only
print "\n\n"
print "  STRIKE ,    LAST"
for sub_list in strike_last_list:
        print sub_list
print "\n\n"

#Get closing price of last market trading day (User Specified)
price = web.DataReader('AAPL', 'google', date, date)['Close'].item()
print price
print "\n\n"

'''

########################

########################

#A bank consists of a interest rate.
class Bank(object):
	def __init__(self, r):
		self.r = r
		self.d_factor = 1 / (1+self.r)

#A stock consists of an initial value, up/down factor, and RNPs. Note that a security also has a bank it tries to beat.
class Security(object):
	def __init__(self, bank, s_0, u, d):
		self.bank = bank
		self.s_0 = s_0
		self.u = u
		self.d = d
		self.rnp = ((1+bank.r) - d) / (u-d)
		self.rnq = (u - (1+bank.r)) / (u-d)

#A derivative security consists of an underlying security, a strike price. an expieration date, and a function to determine its value.	
class DerivSecurity(Security):
	def __init__(self, security, k, t, f):
		self.security = security
		self.k = k
		self.f = f
		self.t = t

#A put option is a derivative security whos value function if givien by (k - s)^+.
class PutOption(DerivSecurity):
	def __init__(self, security, k, t):
		DerivSecurity.__init__(self, security, k, t, lambda x,y: max(y-x, 0))

#A model consists of a bank, a security, derivative securities, and its number of periods.
class Model(object):
	def __init__(self, bank, security, d_security, n):
		self.bank = bank
		self.security = security
		self.d_security = d_security
		self.n = n

		#Fill security matrix: expands tree using up and down factors.
		security.matrix = [[0 for x in range(self.n+1)] for y in range(self.n+1)]
		for i in range(self.n+1):
			for j in range(self.n+1):
				if i + j <= self.n:
					security.matrix[i][j] = float(pow(security.d, i) * pow(security.u, j) * security.s_0)
				else: 
					security.matrix[i][j] = float(0)

		#Fill each derive security matrix in two steps: 1. determine value at time expieration, 2. do backward induction to compute value at all other times.
		for m in range(len(d_security)):
			d_security[m].matrix =  [[0 for x in range(self.n+1)] for y in range(self.n+1)]
			for i in range(self.n+1):
				for j in range(self.n+1):
					if i+j == d_security[m].t:
						d_security[m].matrix[i][j] = float(d_security[m].f(security.matrix[i][j], d_security[m].k)) 
					else:
						d_security[m].matrix[i][j] = float(0)

			time = d_security[m].t - 1
			while time >= 0:
				for i in range(self.n+1):
					for j in range(self.n+1):
						if i+j == time:
							d_security[m].matrix[i][j] = bank.d_factor * (security.rnp * d_security[m].matrix[i][j+1] + security.rnq * d_security[m].matrix[i+1][j])
				time -=1


#A functions for printing matricies with float values.
def matrix_print(matrix):
	for row in range(len(matrix)):
		#each value takes up 9 spaces, and displays up to 5 decimal places
		print(" ".join(['{:10.5}'.format(i) for i in matrix[row]])) 
	print("\n\n\n")


def minimize(quo, model, ep, tol, timeout):
	#set u,d,r current model to given model
	curr_model = model
	#initial [u,d,r].
	curr_vect = [curr_model.security.u, curr_model.security.d, curr_model.bank.r]
	quo_mag = sum([pow(quo[i], 2) for i in range(len(quo))])
	#initial error
	curr_error = sum([pow(quo[m] - curr_model.d_security[m].matrix[0][0], 2) / quo_mag for m in range(len(curr_model.d_security))])
	#sets initial u,d,r and initial error as minimums
	min_udr = [curr_vect[i] for i in range(len(curr_vect))]
	min_error = curr_error
	#prints initial [u,d,r].
	print('Initial [u, d, r]: ' + str(curr_vect))
	#prints quotes prices, initial estimated prices, and initial error.
	print('Quoted prices: ' + str(quo) + ", Initial estimated prices: " + str([curr_model.d_security[m].matrix[0][0] for m in range(len(curr_model.d_security))])+ ', Initial error: '+str(curr_error)+"\n")
	#counts till timeout time.
	iterations = 1

	#make empty lists so that we can fill them later
	u_epp_bank = range(len(curr_model.d_security))
	u_epp_security = range(len(curr_model.d_security))
	u_epp_d_security = range(len(curr_model.d_security))
	u_epp_model = range(len(curr_model.d_security))

	u_epm_bank = range(len(curr_model.d_security))
	u_epm_security = range(len(curr_model.d_security))
	u_epm_d_security = range(len(curr_model.d_security))
	u_epm_model = range(len(curr_model.d_security))

	d_epp_bank = range(len(curr_model.d_security))
	d_epp_security = range(len(curr_model.d_security))
	d_epp_d_security = range(len(curr_model.d_security))
	d_epp_model = range(len(curr_model.d_security))

	d_epm_bank = range(len(curr_model.d_security))
	d_epm_security = range(len(curr_model.d_security))
	d_epm_d_security = range(len(curr_model.d_security))
	d_epm_model = range(len(curr_model.d_security))

	r_epp_bank = range(len(curr_model.d_security))
	r_epp_security = range(len(curr_model.d_security))
	r_epp_d_security = range(len(curr_model.d_security))
	r_epp_model = range(len(curr_model.d_security))

	r_epm_bank = range(len(curr_model.d_security))
	r_epm_security = range(len(curr_model.d_security))
	r_epm_d_security = range(len(curr_model.d_security))
	r_epm_model = range(len(curr_model.d_security))


	#iterates while error is greater than tolerance, and timeout time not met.
	while curr_error > tol and iterations <= timeout:
		print('iteration '+str(iterations))

		#calculations for gradient vector for each d security - iterate through all m of them and get new security price v_0 for each d security
		for m in range(len(curr_model.d_security)):
			u_epp_bank[m] = Bank(curr_model.bank.r)
			u_epp_security[m] = Security(u_epp_bank[m], model.d_security[m].security.s_0, curr_model.d_security[m].security.u + ep, curr_model.d_security[m].security.d)
			u_epp_d_security[m] = DerivSecurity(u_epp_security[m], curr_model.d_security[m].k, curr_model.d_security[m].t, curr_model.d_security[m].f)
			u_epp_model[m] = Model(u_epp_bank[m], u_epp_security[m], [u_epp_d_security[m]], curr_model.n)

			u_epm_bank[m] = Bank(curr_model.bank.r)
			u_epm_security[m] = Security(u_epm_bank[m], curr_model.d_security[m].security.s_0, curr_model.d_security[m].security.u - ep, curr_model.d_security[m].security.d)
			u_epm_d_security[m] = DerivSecurity(u_epm_security[m], curr_model.d_security[m].k, curr_model.d_security[m].t, curr_model.d_security[m].f)
			u_epm_model[m] = Model(u_epm_bank[m], u_epm_security[m], [u_epm_d_security[m]], curr_model.n)

			d_epp_bank[m] = Bank(curr_model.bank.r)
			d_epp_security[m] = Security(d_epp_bank[m], curr_model.d_security[m].security.s_0, curr_model.d_security[m].security.u, curr_model.d_security[m].security.d + ep)
			d_epp_d_security[m] = DerivSecurity(d_epp_security[m], curr_model.d_security[m].k, curr_model.d_security[m].t, curr_model.d_security[m].f)
			d_epp_model[m] = Model(d_epp_bank[m], d_epp_security[m], [d_epp_d_security[m]], curr_model.n)

			d_epm_bank[m] = Bank(curr_model.bank.r)
			d_epm_security[m] = Security(d_epm_bank[m], curr_model.d_security[m].security.s_0, curr_model.d_security[m].security.u, curr_model.d_security[m].security.d - ep)
			d_epm_d_security[m] = DerivSecurity(d_epm_security[m], curr_model.d_security[m].k, curr_model.d_security[m].t, curr_model.d_security[m].f)
			d_epm_model[m] = Model(d_epm_bank[m], d_epm_security[m], [d_epm_d_security[m]], curr_model.n)

			r_epp_bank[m] = Bank(curr_model.bank.r + ep)
			r_epp_security[m] = Security(r_epp_bank[m], curr_model.d_security[m].security.s_0, curr_model.d_security[m].security.u, curr_model.d_security[m].security.d)
			r_epp_d_security[m] = DerivSecurity(r_epp_security[m], curr_model.d_security[m].k, curr_model.d_security[m].t, curr_model.d_security[m].f)
			r_epp_model[m] = Model(r_epp_bank[m], r_epp_security[m], [r_epp_d_security[m]], curr_model.n)

			r_epm_bank[m] = Bank(curr_model.bank.r - ep)
			r_epm_security[m] = Security(r_epm_bank[m], curr_model.d_security[m].security.s_0, curr_model.d_security[m].security.u, curr_model.d_security[m].security.d)
			r_epm_d_security[m] = DerivSecurity(r_epm_security[m], curr_model.d_security[m].k, curr_model.d_security[m].t, curr_model.d_security[m].f)
			r_epm_model[m] = Model(r_epm_bank[m], r_epm_security[m], [r_epm_d_security[m]], curr_model.n)

		#construct plus and minus epsilon vector for computing gradient
		epp_vect = [sum([u_epp_model[m].d_security[0].matrix[0][0] for m in range(len(curr_model.d_security))]), sum([d_epp_model[m].d_security[0].matrix[0][0] for m in range(len(curr_model.d_security))]), sum([r_epp_model[m].d_security[0].matrix[0][0] for m in range(len(curr_model.d_security))])]
		epm_vect = [sum([u_epm_model[m].d_security[0].matrix[0][0] for m in range(len(curr_model.d_security))]), sum([d_epm_model[m].d_security[0].matrix[0][0] for m in range(len(curr_model.d_security))]), sum([r_epm_model[m].d_security[0].matrix[0][0] for m in range(len(curr_model.d_security))])]
		grad_mult = sum([(quo[m] - curr_model.d_security[m].matrix[0][0]) / ep for m in range(len(curr_model.d_security))])
		#calculate grad vector in direction towards min
		grad_vector = [grad_mult * (epp_vect[i] - epm_vect[i]) for i in range(len(epp_vect))]
		

		#get new [u,d,r]
		next_vect = [curr_vect[i] + grad_vector[i] for i in range(len(grad_vector))]

		#rescales gradient by 10 if new [u,d,r] out of AF zone
		while next_vect[1] < 0 or (1 + next_vect[2]) < next_vect[1] or next_vect[0] < (1 + next_vect[2]):
			grad_vector = [(grad_vector[i] / 10) for i in range(len(grad_vector))]
			print("new gradient: " + str(grad_vector))
			
			#ignore this lol
			'''
			#if gradient gets to small
			if abs(grad_vector[0]) < pow(10,-15) and abs(grad_vector[1]) < pow(10,-15) and abs(grad_vector[2]) < pow(10,-15):
				print ("grad to small")	
				iterations = timeout
				next_vect = [curr_vect[i] for i in range(len(curr_vect))] 
			else:
				#print('grad vect: '+str(grad_vector))
				next_vect = [curr_vect[i] + grad_vector[i] for i in range(len(grad_vector))]
			'''
			next_vect = [curr_vect[i] + grad_vector[i] for i in range(len(grad_vector))] 


		#set current [u,d,r] to new [u,d,r]
		curr_vect = [next_vect[i] for i in range(len(next_vect))]
		#makes new current model - i.e new V_0 based current u,d,r found.
		curr_bank = Bank(curr_vect[2])
		curr_sec = Security(curr_bank, curr_model.security.s_0, curr_vect[0], curr_vect[1])
		curr_d_sec = [DerivSecurity(curr_sec, curr_model.d_security[m].k, curr_model.d_security[m].t, curr_model.d_security[m].f) for m in range(len(curr_model.d_security))]
		curr_model = Model(curr_bank, curr_sec, curr_d_sec, model.n)

		#calculate error from this iteration 
		error = sum([pow(quo[m] - curr_model.d_security[m].matrix[0][0], 2) / quo_mag for m in range(len(curr_model.d_security))])
		
		#if error is less than last, we set it as min and set the current u,d,r as mins
		if error < curr_error:
			min_error = error
			min_udr = [curr_vect[i] for i in range(len(curr_vect))]

		#set the current error to the computer error from this iteration
		curr_error = error
 
		#prints new current u,d,r
		print('New [u,d,r]: '+str(curr_vect))
		#prints quoted prices, current estimated prices, and current error
		print('Quoted prices: ' + str(quo) + ", New estimated prices: " + str([curr_model.d_security[m].matrix[0][0] for m in range(len(curr_model.d_security))]) + ', New error: '+str(curr_error))
		#prints min u,d,r and min error from iterations fo far
 		print("Min error: " +str(min_error) + ", Best [u,d,r]: " + str(min_udr)+"\n")

		#counts interations up to timeout
		iterations += 1

#INPUTS HERE!!!!
#enter initial interest rate
r_0 = 0.001
#enter initial up factor
u_0 = 1.01
#enter initial down factor
d_0 = .99
#speciiy periods in model
periods = 15
#specify maturity for puts
maturity = 15
#specify intial stock price
s_0= 81.61
#specify quote prices for puts
put_options_quoted = [0.55, 1.31, 0.05]
#specify strike price for corresponding put
put_options_stike = [85, 82.5, 90]
#specify size of step to take at each approximation
epsilon = 0.00001
#specify error tolerance
tol = 0.00001
#specify max number of iterations until timeout
timeout = 500



#ignore this stuff lol
put_options = [0,0]
put_options[0] = put_options_quoted
put_options[1] = put_options_stike
#set initial interest rate
bank = Bank(r_0)
#underlying bank / todays value / up factor / down factor
stock = Security(bank, s_0, u_0, d_0)
#underlying stock / strike price / experation date
puts = [PutOption(stock, put_options[1][i], maturity) for i in range(len(put_options[1]))]
#underlying bank / underlying stock / underlying derivative security / number of periods
model = Model(bank, stock, puts, periods)
#prints value matrix for stock
matrix_print(stock.matrix)
#prints value matrix for each derivative security
for m in range(len(puts)):
	matrix_print(puts[m].matrix)
#quoted / model / epsilon / tolerance / timeout
minimize(put_options[0], model, epsilon, tol, timeout)












		













