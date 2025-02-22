# The denoising autencoder has one hidden layer, and a softmax output layer.

'''
This file implements a two layer neural network for a binary classifier

Manish Seal
mseal1@asu.edu
'''

import numpy as np
from load_mnist import mnist
import matplotlib.pyplot as plt
import pdb
import sys, ast
import pickle

#np.random.seed(81)
epsilon = 0.0000000
alpha = 1

def relu(Z):
    '''
    computes relu activation of Z

    Inputs: 
        Z is a numpy.ndarray (n, m)

    Returns: 
        A is activation. numpy.ndarray (n, m)
        cache is a dictionary with {"Z", Z}
    '''
    
    A = np.maximum(0,Z)
    cache = {}
    cache["Z"] = Z
    return A, cache

def relu_der(dA, cache):
    '''
    computes derivative of relu activation

    Inputs: 
        dA is the derivative from subsequent layer. numpy.ndarray (n, m)
        cache is a dictionary with {"Z", Z}, where Z was the input 
        to the activation layer during forward propagation

    Returns: 
        dZ is the derivative. numpy.ndarray (n,m)
    '''
    dZ = np.array(dA, copy=True)
    Z = cache["Z"]
    dZ[Z<0] = 0
    return dZ

def tanh(Z):
    '''
    computes tanh activation of Z

    Inputs: 
        Z is a numpy.ndarray (n, m)

    Returns: 
        A is activation. numpy.ndarray (n, m)
        cache is a dictionary with {"Z", Z}
    '''
    A = np.tanh(Z*alpha)
    cache = {}
    cache["Z"] = Z
    return A, cache

def tanh_der(dA, cache):
    '''
    computes derivative of tanh activation

    Inputs: 
        dA is the derivative from subsequent layer. numpy.ndarray (n, m)
        cache is a dictionary with {"Z", Z}, where Z was the input 
        to the activation layer during forward propagation

    Returns: 
        dZ is the derivative. numpy.ndarray (n,m)
    '''
    A, cache = tanh(cache["Z"])

    dZ = dA * (1 - A * A)*alpha


    return dZ

def sigmoid(Z):
    '''
    computes sigmoid activation of Z

    Inputs: 
        Z is a numpy.ndarray (n, m)

    Returns: 
        A is activation. numpy.ndarray (n, m)
        cache is a dictionary with {"Z", Z}
    '''
    
    A = 1/(1+np.exp(-Z*alpha))
    cache = {}
    cache["Z"] = Z
    return A, cache

def sigmoid_der(dA, cache):
    '''
    computes derivative of sigmoid activation

    Inputs: 
        dA is the derivative from subsequent layer. numpy.ndarray (n, m)
        cache is a dictionary with {"Z", Z}, where Z was the input 
        to the activation layer during forward propagation

    Returns: 
        dZ is the derivative. numpy.ndarray (n,m)
    '''
    A, cache = sigmoid(cache["Z"])
    dZ = dA * A * (1 - A) * alpha
    return dZ

def initialize_2layer_weights(n_in, n_h, n_fin):
    '''
    Initializes the weights of the 2 layer network

    Inputs: 
        n_in input dimensions (first layer)
        n_h hidden layer dimensions
        n_fin final layer dimensions

    Returns:
        dictionary of parameters
    '''
    # initialize network parameters
    
    np.random.seed(81)
    W1 = np.random.rand(n_h, n_in)*0.01
    b1 = np.random.rand(n_h, 1)*0.01
    W2 = np.random.rand(n_fin, n_h)*0.01
    b2 = np.random.rand(n_fin, 1)*0.01


    parameters = {}
    parameters["W1"] = W1
    parameters["b1"] = b1
    parameters["W2"] = W2
    parameters["b2"] = b2

    return parameters

def linear_forward(A, W, b):
    '''
    Input A propagates through the layer 
    Z = WA + b is the output of this layer. 

    Inputs: 
        A - numpy.ndarray (n,m) the input to the layer
        W - numpy.ndarray (n_out, n) the weights of the layer
        b - numpy.ndarray (n_out, 1) the bias of the layer

    Returns:
        Z = WA + b, where Z is the numpy.ndarray (n_out, m) dimensions
        cache - a dictionary containing the inputs A, W and b
        to be used for derivative
    '''

    Z = np.dot(W,A) + b

    cache = {}
    cache["A"] = A
    return Z, cache

def layer_forward(A_prev, W, b, activation):
    '''
    Input A_prev propagates through the layer and the activation

    Inputs: 
        A_prev - numpy.ndarray (n,m) the input to the layer
        W - numpy.ndarray (n_out, n) the weights of the layer
        b - numpy.ndarray (n_out, 1) the bias of the layer
        activation - is the string that specifies the activation function

    Returns:
        A = g(Z), where Z = WA + b, where Z is the numpy.ndarray (n_out, m) dimensions
        g is the activation function
        cache - a dictionary containing the cache from the linear and the nonlinear propagation
        to be used for derivative
    '''
    Z, lin_cache = linear_forward(A_prev, W, b) #lin_cache stores this A_prev
    if activation == "sigmoid":
        A, act_cache = sigmoid(Z) #act_cache stores the Z
    elif activation == "tanh":
        A, act_cache = tanh(Z)
    elif activation == "relu":
        A, act_cache = relu(Z)
    
    cache = {}
    cache["lin_cache"] = lin_cache
    cache["act_cache"] = act_cache

    return A, cache

"""
def cost_estimate(A2, Y):
    '''
    Estimates the cost with prediction A2

    Inputs:
        A2 - numpy.ndarray (1,m) of activations from the last layer
        Y - numpy.ndarray (1,m) of labels
    
    Returns:
        cost of the objective function
    '''
    ### CODE HERE

    m = A2.shape[1]
    #print("inside cost estimate")
    #print("m = ",m)
    cost = np.sum(Y*np.log(A2) + (1-Y)*np.log(1 - A2))/(-m)
    return cost
"""

def linear_backward(dZ, cache, W, b):
    '''
    Backward propagation through the linear layer

    Inputs:
        dZ - numpy.ndarray (n,m) derivative dL/dz 
        cache - a dictionary containing the inputs A
            where Z = WA + b,    
            Z is (n,m); W is (n,p); A is (p,m); b is (n,1)
        W - numpy.ndarray (n,p)  
        b - numpy.ndarray (n, 1)

    Returns:
        dA_prev - numpy.ndarray (p,m) the derivative to the previous layer
        dW - numpy.ndarray (n,p) the gradient of W 
        db - numpy.ndarray (n, 1) the gradient of b
    '''
    # CODE HERE

    dA_prev = np.dot(W.T,dZ)
    dW = np.dot(dZ, cache["A"].T)
    db = np.sum(dZ, axis=1, keepdims=True)

    return dA_prev, dW, db

def layer_backward(dA, cache, W, b, activation):
    '''
    Backward propagation through the activation and linear layer

    Inputs:
        dA - numpy.ndarray (n,m) the derivative to the previous layer
        cache - dictionary containing the linear_cache and the activation_cache
        W - numpy.ndarray (n,p)  
        b - numpy.ndarray (n, 1)
    
    Returns:
        dA_prev - numpy.ndarray (p,m) the derivative to the previous layer
        dW - numpy.ndarray (n,p) the gradient of W 
        db - numpy.ndarray (n, 1) the gradient of b
    '''
    lin_cache = cache["lin_cache"] #contains the A that comes to this layer
    act_cache = cache["act_cache"] #contains the Z that is calculated in this layer

    if activation == "sigmoid":
        dZ = sigmoid_der(dA, act_cache)
    elif activation == "tanh":
        dZ = tanh_der(dA, act_cache)
    elif activation == "relu":
        dZ = relu_der(dA, act_cache)
    dA_prev, dW, db = linear_backward(dZ, lin_cache, W, b)
    return dA_prev, dW, db

"""
def loss_layer(A2, Y):
    '''
    The last layer for calculating the dA_lastLayer

    Inputs:
        A2 - the final output of the network
        Y - original class labels
    Output:
        dA2 - the derivative of the final A2
    '''
    m = A2.shape[1]
    dA2 = ( ( Y / (A2) ) - ( (1 - Y) / (1 - A2) ) )/(-m)

    return dA2
"""

def quadratic_loss_layer(AL, Y):
    """
    The last loss layer for calculating the quadratic loss and returning the derivative
    
    Inputs:
        A: the output of the last layer
        Y: the original Y required
    
    """
    k , m = AL.shape
    l = AL-Y
    L = (l*l)/(2*m*1.0)
    cost = np.sum(L)
    
    dAL = l/(m)
    
    return dAL, cost
    


def denoise(X, parameters, activations):
    """
    Input:
        X: an array of shape [n, m], containing the noisy images to be de-noised
        parameter: a dictionary containing the weights and biases for the different layers
                a dictionary like {"W1":[...], "b1":[...]..}
    Output:
        A2: the denoised version as predicted by the autoencoder
    """
    A0=X
    A1, cache_ = layer_forward(A_prev = A0, W = parameters["W1"], b = parameters["b1"], activation=activations[0] )
    A2, cache_ = layer_forward(A_prev = A1, W = parameters["W2"], b = parameters["b2"], activation=activations[1] )
    
    return A2
    

def two_layer_network(X, Y, X_validation, Y_validation, net_dims, num_iterations=20, learning_rate=0.1,
                      activations=["tanh", "sigmoid"]
                     ):
    '''
    Creates the 2 layer network and trains the network

    Inputs:
        X - numpy.ndarray (n,m) of training data
        Y - numpy.ndarray (1,m) of training data labels
        net_dims - tuple of layer dimensions
        num_iterations - num of epochs to train
        learning_rate - step size for gradient descent
    
    Returns:
        costs - list of costs over training
        parameters - dictionary of trained network parameters
    '''
    n_in, n_h, n_fin = net_dims
    parameters = initialize_2layer_weights(n_in, n_h, n_fin)
    
    
    A0 = X
    costs = []
    validation_costs = []
    logs = []
    for ii in range(num_iterations):
        # Forward propagation
        A1, cache1 = layer_forward(A_prev = A0, W = parameters["W1"], b = parameters["b1"], activation=activations[0] )
        A2, cache2 = layer_forward(A_prev = A1, W = parameters["W2"], b = parameters["b2"], activation=activations[1] )
        
        A1_validation, cache_validation = layer_forward(A_prev = X_validation,
                                                         W = parameters["W1"],
                                                         b = parameters["b1"],
                                                         activation=activations[0] )
        A2_validation, cache_validation = layer_forward(A_prev = A1_validation,
                                                         W = parameters["W2"],
                                                         b = parameters["b2"],
                                                         activation=activations[1] )
        
        
        

        # cost estimation
        dA2, cost = quadratic_loss_layer(AL=A2, Y=Y)
        dA2_validation, validation_cost = quadratic_loss_layer(AL = A2_validation , Y=Y_validation)
        #print("at i = ",ii, "cost = ", cost)
        
        # Backward Propagation
        
        dA1, dW2, db2 = layer_backward(dA2,
                                       cache2,
                                       W = parameters["W2"],
                                       b = parameters["b2"],
                                       activation = activations[1]
                                      )
        dA0, dW1, db1 = layer_backward(dA1,
                                       cache1,
                                       W = parameters["W1"],
                                       b = parameters["b1"],
                                       activation = activations[0]
                                      )

        #update parameters

        parameters["W1"] -= learning_rate*dW1
        parameters["b1"] -= learning_rate*db1
        parameters["W2"] -= learning_rate*dW2
        parameters["b2"] -= learning_rate*db2
        
        
        
        


        if ii % 10 == 0:
            costs.append(cost)
            validation_costs.append(validation_cost)
        if ii % 10 == 0:
            str1 = "Cost at iteration %i is: %f" %(ii, cost)
            str2 = "Validation Cost at iteration %i is: %f" %(ii, validation_cost)
            print(str1)
            print(str2)
            logs.append(str1)
            logs.append(str2)
    
    return costs, validation_costs, parameters, logs

def main():
    # Denote the Network Dimensions here
    net_dims=[784, 1200, 784]
    
    
    #Provide the address to the noisy data pickle dump 
    data_file = "fashion_train_validation_test_split_data_noTr_50000_noTs_10000_digits_[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]_noise_0_2.txt"
    data = {}
    with open(data_file, "rb") as fp:
        data = pickle.load(fp)
        
    print("Data Loading done")
        
    noisy_train_data = data["noisy_train_data"]
    train_data = data["train_data"]
    train_label = data["train_label"]
    noisy_validation_data = data["noisy_validation_data"]
    validation_data = data["validation_data"]
    validation_label = data["validation_label"]
    noisy_test_data = data["noisy_test_data"]
    test_data = data["test_data"]
    test_label = data["test_label"]
    
    digit_range = [0,1,2,3,4,5,6,7,8,9]
    
    unique_test_image_index = []
    for ll in digit_range:
        idx = np.where(test_label == ll)
        unique_test_image_index.append(idx[1][0])
    
    
    
        
    
    n_in, m = noisy_train_data.shape
    n_h = net_dims[1]
    n_fin = net_dims[2]
    # initialize learning rate and num_iterations
    learning_rate = 0.1
    num_iterations = 601
    activations = ["tanh","sigmoid"]
    
    
                
    
    print("network dimensions = ", net_dims)

    costs, validation_costs, parameters, logs = two_layer_network(X=noisy_train_data,
                                                            Y=train_data,
                                                            X_validation=noisy_validation_data,
                                                            Y_validation=validation_data,
                                                            net_dims=net_dims,
                                                            num_iterations=num_iterations,
                                                            learning_rate=learning_rate,
                                                            activations=activations
                                                           )
    
    # compute the accuracy for training set and testing set
    train_Pred = denoise(noisy_train_data, parameters, activations)
    test_Pred = denoise(noisy_test_data, parameters, activations)
    
    dA_, train_cost = quadratic_loss_layer(AL=train_Pred, Y=train_data)
    dA_, test_cost = quadratic_loss_layer(AL=test_Pred, Y=test_data)
    
    print("train_pred shape:",train_Pred.shape)
    print("test_pred shape:",test_Pred.shape)
    
    
    
    print("Cost for training set is {0:0.3f} ".format(train_cost))
    print("Cost for testing set is {0:0.3f} ".format(test_cost))
    fig_name = "outputs/fashion/figure_"+str(net_dims)+"_activations_"+str(activations)+\
                    "_lr_"+str(learning_rate)+\
                    "_digits_"+str(len(digit_range))+\
                    "_ni_"+str(num_iterations)+\
                    "_train_size_"+str(len(train_data))
    
    parameter_file = "outputs/fashion/parameters_"+str(net_dims)+"_activations_"+\
                        str(activations)+"_lr_"+str(learning_rate)+\
                        "_digits_"+str(len(digit_range))+\
                        "_ni_"+str(num_iterations)+\
                    "_train_size_"+str(len(train_data))
    
    log_file = "outputs/fashion/logs_"+str(net_dims)+"_activations_"+str(activations)+"_lr_"+str(learning_rate)+\
                        "_digits_"+str(len(digit_range))+\
                        "_ni_"+str(num_iterations)+\
                    "_train_size_"+str(len(train_data))
    fig_name = fig_name.replace(".","_")
    parameter_file = parameter_file.replace(".", "_")
    log_file = log_file.replace(".","_")
    parameter_file += ".params"
    log_file += ".log"
    
    with open(parameter_file, "wb") as fp:
        pickle.dump(parameters, fp)
    
    with open(log_file, "w") as fp:
        for i in logs:
            fp.write(i)
    
    
    
    
    count = 1
    num_digits = len(digit_range)
    plt.figure( figsize=(5*num_digits, 10) )
    
    for i in unique_test_image_index:
        plt.subplot(num_digits,3,count)
        plt.imshow(test_data[:,i].reshape(28, -1), cmap="gray")
        count += 1
        plt.subplot(num_digits,3,count)
        plt.imshow(noisy_test_data[:,i].reshape(28, -1), cmap="gray")
        count += 1
        plt.subplot(num_digits,3,count)
        plt.imshow(test_Pred[:,i].reshape(28, -1), cmap="gray")
        count += 1
        
    plt.savefig(fig_name)
    plt.show()
    
    
    


if __name__ == "__main__":
    main()

