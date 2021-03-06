from pybrain.tools.shortcuts import buildNetwork
from pybrain.supervised.trainers import BackpropTrainer
from pybrain.datasets import SupervisedDataSet,UnsupervisedDataSet
from pybrain.structure import LinearLayer
from pyspark.sql import SparkSession
from pyspark import SparkContext, SparkConf

import math
import multiprocessing
import numpy
import sys
import time

window = 200
filename = "./data/signal3/signal"
#for samples in (40):
samples = 40
#for num_cores in (4):
num_cores = 2

def partialTraining(index, length, result_queue):
	#change t_set to RDD
	actualLength = 0
	t_set = []
	for i in range (index, index+length):
		try:
			t_set.append( numpy.loadtxt(filename+str(i+1)+".txt") )
			actualLength += 1
		except Exception as e:
			break
			

	
	d_set = SupervisedDataSet(window, window)
	for i in range (0, actualLength-1):
		d_set.addSample(t_set[i], t_set[i+1])

	network = buildNetwork(window, window-1, window, outclass=LinearLayer,bias=True, recurrent=True)
	bpTrainer = BackpropTrainer(network, d_set)
	bpTrainer.trainEpochs(100)

	t_s = UnsupervisedDataSet(window,)
	#add the sample to be predicted
	t_s.addSample(t_set[actualLength-1])

	result = network.activateOnDataset(t_s)
	result_queue.put(result[0])

############MAP##############################################
def training(t_set):
	d_set = SupervisedDataSet(window, window)
	for i in len(t_set):
		d_set.addSample(t_set[i], t_set[i+1])
		
	network = buildNetwork(window, window-1, window, outclass=LinearLayer,bias=True, recurrent=True)
	bpTrainer = BackpropTrainer(network, d_set)
	bpTrainer.trainEpochs(100)
	
	t_s = UnsupervisedDataSet(window,)
	#add the sample to be predicted
	t_s.addSample(t_set[actualLength-1])

	result = network.activateOnDataset(t_s)
	return result


###########REDUCE#############################################
def final_training(results):
	finalTrainingSet = []
	size = num_cores
	ds = SupervisedDataSet(window, window)

	while not results.empty():
	    finalTrainingSet.append(results.get())

	for i in range (size-1):
	    ds.addSample(finalTrainingSet[i], finalTrainingSet[i+1])

	net = buildNetwork(window, window-1, window, outclass=LinearLayer,bias=True, recurrent=True)
	trainer = BackpropTrainer(net, ds)
	trainer.trainEpochs(100)

	ts = UnsupervisedDataSet(window,)
	ts.addSample(finalTrainingSet[size-1])

	finalResult = net.activateOnDataset(ts)
	return finalResult
	



if __name__ == "__main__":

	conf = SparkConf().setAppName("rnn_spark")
	sc = SparkContext(conf=conf)


	for tm in range(1):
		t0 = time.time()
		#jobs = []
		#tSet_length = 1024 / num_cores
		'''
		tSet_length = int(math.ceil(samples / num_cores))
		curr_index = 0
		results = multiprocessing.Queue()

		for i in range(num_cores):
		    p = multiprocessing.Process(target=partialTraining, args=(curr_index, tSet_length, results))
		    jobs.append(p)
		    curr_index += tSet_length
		    
		for proc in jobs:
		    proc.start()

		for proc in jobs:
		    proc.join()
		'''
		#############map#################
		#read files

		t_set = []
		for i in range (1, samples+1):
			try:
				t_set.append( numpy.loadtxt(filename+str(i+1)+".txt") )
				#actualLength += 1
			except Exception as e:
				break
				
		rdd = sc.parallelize(t_set, num_cores)


		intermediate_result = rdd.map(training).collect()
		
		final_result = intermediate_result.reduce(final_training).collect()
		#############################

		
'''
		finalTrainingSet = []
		size = num_cores
		ds = SupervisedDataSet(window, window)

		while not results.empty():
		    finalTrainingSet.append(results.get())

		for i in range (size-1):
		    ds.addSample(finalTrainingSet[i], finalTrainingSet[i+1])

		net = buildNetwork(window, window-1, window, outclass=LinearLayer,bias=True, recurrent=True)
		trainer = BackpropTrainer(net, ds)
		trainer.trainEpochs(100)

		ts = UnsupervisedDataSet(window,)
		ts.addSample(finalTrainingSet[size-1])

		finalResult = net.activateOnDataset(ts)
'''

		t1 = time.time()

		print "which loop: ", tm, "number of samples tested: ", samples, 
		print "number of cores: ", num_cores, "running time: ", t1 - t0

		#for elem in finalResult[0]:
		#    print elem
                #IMPORTANT: MAP REDUCE HERE 
                #WORK TBD
                spark.stop()
'''
ds = SupervisedDataSet(window, window)

#filename = "./data/cassandra_data_new/cassandra_new"

#train1 = open(filename+"1",'rU').read().split('\n')
#train2 = open(filename+"2",'rU').read().split('\n')
#train1 = numpy.loadtxt(filename+"1")
#train2 = numpy.loadtxt(filename+"2")
#train3 = numpy.loadtxt(filename+"3")
#train4 = numpy.loadtxt(filename+"4")
#train5 = numpy.loadtxt(filename+"5")
#train6 = numpy.loadtxt(filename+"6")
#train7 = numpy.loadtxt(filename+"7")

trainingSet = []
for i in range (1, 1001):
	trainingSet.append( numpy.loadtxt(filename+str(i)+".txt") )

for i in range (0, 999):
	ds.addSample(trainingSet[i], trainingSet[i+1])

#ds.addSample(train1,train2)
#ds.addSample(train2,train3)
#ds.addSample(train3,train4)
#ds.addSample(train4,train5)
#ds.addSample(train5,train6)
#ds.addSample(train6,train7)
 
 
net = buildNetwork(window, window-1, window, outclass=LinearLayer,bias=True, recurrent=True)
trainer = BackpropTrainer(net, ds)
trainer.trainEpochs(100)

ts = UnsupervisedDataSet(window,)
#add the sample to be predicted
ts.addSample(trainingSet[999])

result = net.activateOnDataset(ts)
for elem in result[0]:
    print elem
'''

'''
window = 110
ds = SupervisedDataSet(window, window)

filename = "./data/mongo_data/mongo_"

#train1 = open(filename+"1",'rU').read().split('\n')
#train2 = open(filename+"2",'rU').read().split('\n')
train1 = numpy.loadtxt(filename+"1")
train2 = numpy.loadtxt(filename+"2")
train3 = numpy.loadtxt(filename+"3")
train4 = numpy.loadtxt(filename+"4")
train5 = numpy.loadtxt(filename+"5")
train6 = numpy.loadtxt(filename+"6")
train7 = numpy.loadtxt(filename+"7")
train8 = numpy.loadtxt(filename+"8")
train9 = numpy.loadtxt(filename+"9")
train10 = numpy.loadtxt(filename+"10")
train11 = numpy.loadtxt(filename+"11")
train12 = numpy.loadtxt(filename+"12")


ds.addSample(train1,train2)
ds.addSample(train2,train3)
ds.addSample(train3,train4)
ds.addSample(train4,train5)
ds.addSample(train5,train6)
ds.addSample(train6,train7)
ds.addSample(train7,train8)
ds.addSample(train8,train9)
ds.addSample(train9,train10)
 
 
net = buildNetwork(window, window-1, window, outclass=LinearLayer,bias=True, recurrent=True)
trainer = BackpropTrainer(net, ds)
trainer.trainEpochs(100)

ts = UnsupervisedDataSet(window,)
#add the sample to be predicted
ts.addSample(train10)

result = net.activateOnDataset(ts)
for elem in result[0]:
        print elem 
        
#cassandra

window = 64
ds = SupervisedDataSet(window, window)

filename = "./data/cassandra_data/cassandra_"

#train1 = open(filename+"1",'rU').read().split('\n')
#train2 = open(filename+"2",'rU').read().split('\n')
train1 = numpy.loadtxt(filename+"1")
train2 = numpy.loadtxt(filename+"2")
train3 = numpy.loadtxt(filename+"3")
train4 = numpy.loadtxt(filename+"4")
train5 = numpy.loadtxt(filename+"5")
train6 = numpy.loadtxt(filename+"6")
train7 = numpy.loadtxt(filename+"7")
train8 = numpy.loadtxt(filename+"8")
train9 = numpy.loadtxt(filename+"9")
train10 = numpy.loadtxt(filename+"10")
train11 = numpy.loadtxt(filename+"11")


ds.addSample(train1,train2)
ds.addSample(train2,train3)
ds.addSample(train3,train4)
ds.addSample(train4,train5)
ds.addSample(train5,train6)
ds.addSample(train6,train7)
ds.addSample(train7,train8)
ds.addSample(train8,train9)
ds.addSample(train9,train10)
 
 
net = buildNetwork(window, window-1, window, outclass=LinearLayer,bias=True, recurrent=True)
trainer = BackpropTrainer(net, ds)
trainer.trainEpochs(100)

ts = UnsupervisedDataSet(window,)
#add the sample to be predicted
ts.addSample(train10)

print("Cassandra...")
result = net.activateOnDataset(ts)
for elem in result[0]:
        print elem
'''
