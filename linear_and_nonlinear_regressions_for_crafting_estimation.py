"""
**Crafting Time Estimation**

Using regressions, of both the linear and non-linear persuasions.  We will be using these to create estimates in the amount of time required to get from a given crafting state to another crafting state, i.e. to produce a heuristic cost for the planning done in homework 2.  


We will be constructing the following models:

1. A linear regression solved via raw matrix operations, as discussed in class
2. A linear regression solved via numpy's library
3. A linear regression solved via Stochastic Gradient Descent with an artificial neural network
4. A linear regression using a deep artificial neural network
5. A non-linear regression using a deep artificial neural network

Finally, the non-linear regression will be used as the heuristic in an A* search of the planning space

Our first step is to read the data in a form that is conducive for regression.  The data is a CSV file where the first row are the names of each column.
"""

import random
import itertools
import time
import heapq
import array
from typing import NamedTuple, Dict, Tuple, Optional, Sequence, List, Set, FrozenSet
import json
import torch
import matplotlib.pyplot as plt
import numpy as np
!wget https: // raw.githubusercontent.com/adamsumm/AI_Minecraft_Assignments/master/CraftingRegressionEstimation/crafting_times.csv

# Open the file
with open('crafting_times.csv', 'r') as infile:
    # Get the header line
    header = infile.readline().rstrip().split(',')
    data = []
    # Read it in
    for line in infile:
        data.append([float(s) for s in line.rstrip().split(',')])
    # turn our list of lists into a numpy array
    data = np.array(data)

print('\n'.join(header))
print(data.shape)

"""We see that the columns are: 
0 -- The time it takes
1-17 -- The initial state
18-35 -- The goal state

Now, we need to construct our X and Y matrices.

Luckily, *slicing* is very easy to do with numpy arrays.  *Slicing* is where we can easily specify how to take subsets of our matrix.  Think of it like indexing into an array, only we can do a lot of them at once.


The general syntax is:

`vector[a:b]`
`matrix[a:b,c:d]` 
`tensor[a:b,c:d,e:f]`

As a note, `a, b, c, d, e, f` are the indices you wish to get -- if `a` is blank it will start from the beginning and if `b` is blank it will go until the end.  Note: these can also be negative, which can be thought of as `n` away from the end.

Some examples:

`data[:,0]` -- Get all of the members of the first column 
`data[:,-1]` -- Get all of the members of the last column
`data[:a,1:]` -- Get the first `a` rows for the 2nd to last columns
`data[a:,1:]` -- Get all of the rows starting at `a` for the 2nd to last columns

As a note, you can get the dimensions of a numpy array by accessing `.shape`, a tuple of the dimensions

#Step 1 -- Set up Matrics  (15 pts)
* Let the first N*validation_split rows be for the validation set 
* and the last N*(1-validation_split) rows be the training data
* At the end of this, you should have:
    
    `Y.shape = (21000, 1)`

    `X.shape = (21000, 34)`

    `Y_validation.shape = (9000, 1)`

    `X_validation.shape = (9000, 34)`
"""

# We want to use a training/validation split to verify we are doing a good job
validation_split = 0.3


# TODO slice the data into the correct matrices for training and validation splits
# Let the first N*validation_split rows be for the validation set
# and the last N*(1-validation_split) rows be the training data

Y = data[0:int((1-validation_split)*len(data)), 0:1]
Y_validation = data[0:int((validation_split)*len(data)), 0:1]

X = data[0:int((1-validation_split)*len(data)), 1:35]
X_validation = data[0:int((validation_split)*len(data)), 1:35]


print("Y.shape = ", Y.shape)
print("X.shape = ", X.shape)
print("Y_validation.shape = ", Y_validation.shape)
print("X_validation.shape = ", X_validation.shape)

"""Now we will use Least Squares Regression to estimate the time cost associated with a given state and end state.  

The least squares regression coefficients can be calculated via the closed form solution:

$\beta =  (X^T X)^{-1} X^T Y$

First try it out with using `np.dot` (anywhere there is a matrix multiplication) and `np.inv` (anywhere there is a matrix inversion. (as a note, matrix transposition is accomplished with `.T`)

Next, compare using `np.linalg.lstsq` -- numpy's built in least squares regression (that is much more stable than using the matrix inversion found here).

#Step 2 -- Perform Linear Regressions (10 pts)
* Write your own version of linear regression using the closed from solution discussed above
* Use the supplied least squares regression that is part of numpy's linear algebra library
* Compare the two
"""

# Least Squares Estimation Goes Here


def calculate_weights_with_linear_algebra(X: np.array, Y: np.array) -> np.array:
    return np.dot(np.linalg.inv(np.dot(X.T, X)), np.dot(X.T, Y))


def calculate_weights_with_library(X: np.array, Y: np.array) -> np.array:
    # Get first element
    return np.linalg.lstsq(X, Y)[0]


B_raw = calculate_weights_with_linear_algebra(X, Y)
B_lstsq = calculate_weights_with_library(X, Y)

# This should be small, mostly in the 1e-13 to 1e-14 range
print(B_raw-B_lstsq)

"""Now we want to test our coefficients and see how well we predict the answer.  To do with we will need to use the weight vector we just learned.  Use `np.dot` to calculate:

$\hat{Y} = X\beta$

We will then calculate the *residual* -- the error that remains between our true times in Y and the calculated times in Yhat.

$resid = Y-\hat{Y} $

We will then use these residuals to come up with a single number that tells us how well we did.  For this, we will be using the Root Mean Squared Error (RMSE)

$RMSE = \sqrt{\frac{1}{N} \sum (y-\hat{y})^2}$

To do this we will use the elementwise multiplication (`a*b` not `np.dot(a,b)`), the square root (`np.sqrt`), and mean (``np.mean``) functions

#Step 3 -- Inference (5 pts)         
* Calculate the predicted values 
* Calculate the error
"""

# TODO: Calculate Yhat, the residuals and RMSE for both the training and validation sets


def calculate_yhat(X: np.array, B: np.array) -> np.array:
    return np.dot(X, B)


def calculate_residuals(Y: np.array, Yhat: np.array) -> np.array:
    return Y-Yhat


def calculate_rmse(residuals: np.array) -> float:
    return np.sqrt(np.mean((residuals*residuals)))


Yhat = calculate_yhat(X, B_raw)
Yhat_validation = calculate_yhat(X_validation, B_raw)

residuals = calculate_residuals(Y, Yhat)
residuals_validation = calculate_residuals(Y_validation, Yhat_validation)

rmse = calculate_rmse(residuals)
rmse_validation = calculate_rmse(residuals_validation)

print('RMSE:', rmse)
print('RMSE Validation:', rmse_validation)


# Now let's plot our points residuals
# Often, we'd like to plot our data, but we have a 30+dimensional space, i.e. one that's hard to visualize
plt.plot(Y, residuals, 'x')
plt.plot(Y_validation, residuals_validation, 'r.')
plt.show()

"""Previously, we learned a weight vector, but because we didn't have a bias term, the weight vector has to go through the origin, which might not be what we want.  Let's try it all again with a bias term this time.

To add a bias term, we will add a new column to our X matrix that is full of constants.  

Does it matter what constant term we choose?

The simplest way to do this is to use `hstack` which takes in a list of matrices and horizontally concatenates them (i.e. adds on new columns -- there exists a `vstack` that adds new rows).  The simpleest way to construct a constant term is to use `np.ones` which takes in a list with the number of ones to make for each dimension.

e.g.
`np.ones([4,2])` will make

1 1

1 1 

1 1

1 1

#Step 4 -- Add a bias term (5 pts)
* Add a bias term to the independent data -- `X`
* Rerun the previous code 
* Compare the new errors to the old
"""

# TODO construct an X matrix with a bias term.

X_with_bias = np.hstack((X, np.ones(X.shape)))
X_validation_with_bias = np.hstack((X_validation, np.ones(X_validation.shape)))

# TODO replace the np.zeros() with the correct code
B_with_bias = calculate_weights_with_library(X_with_bias, Y)

Yhat_with_bias = calculate_yhat(X_with_bias, B_with_bias)
Yhat_validation_with_bias = calculate_yhat(X_validation_with_bias, B_with_bias)

residuals_with_bias = calculate_residuals(Y, Yhat_with_bias)
residuals_validation_with_bias = calculate_residuals(
    Y_validation, Yhat_validation_with_bias)

rmse_with_bias = calculate_rmse(residuals_with_bias)
rmse_validation_with_bias = calculate_rmse(residuals_validation_with_bias)


print('RMSE with bias term:', rmse_with_bias)
print('RMSE Validation with bias term:', rmse_validation_with_bias)

plt.plot(Y, residuals_with_bias, 'x')
plt.plot(Y_validation, residuals_validation_with_bias, 'ro')
plt.show()

"""Now we are going to use artificial neural networks. We are going to be using PyTorch, one of the leading deep learning libraries. 

NOTE: We are going to be doing this in a GPU enabled way, so be sure to make sure your runtime is set to use a GPU -- Runtime > Change Runtime Type > Hardware Accelerator = GPU


First lets use stochastic gradient descent to train a weight vector as we did above.  

PyTorch lets us do this in a number of ways, but we will be doing the easiest possible one.  We are going to construct a `Sequential` model, with a `Linear` layer as its sole argument. `Sequential` can take in an arbitrary number of arguments, where each one is a layer that will be applied in the order that it is passed in.

The parameters you care about for `Linear` are:

`Linear(in_features, out_features, bias=True)`
    
`in_features` is the dimensionality of our input space -- in this case it will be the number of columns found in our X data
`out_features` is the dimensionality of the output space -- in this case, it will be 1 (all of our final `out_features` will always be 1, as our output is the single number we are predicting).  

# Step 5 -- Artificial Neural Network (15 pts)
* Construct a linear regression model in PyTorch
"""

# TODO construct the model
# Define a neural network model as a stack of layers
model = torch.nn.Sequential(
    torch.nn.Linear(X.shape[1], 1, bias=True)
)
model.to('cuda')

print(list(model.parameters()))

"""Given our model, it's now time to train it.  First we need to convert our numpy matrices into PyTorch Tensors.  

Then we need to set up a couple of things --

First, we need to choose which optimizer we are going to use.  For this, let's just go with simple stochastic gradient descent.  `torch.optim.SGD(model.parameters(),lr=LR)` -- you'll need to pick a learning rate.  It's usually best to pick something relatively small, like say 0.01.

Then we need to choose our loss function.  If our goal is to do a regression, we should choose the loss function we chose before, i.e. Mean Square Error --  `torch.nn.MSELoss()`


Then, we need to loop over our dataset a number of times, i.e. a number of *epochs*.  At each step of the process we need to:

1. Zero the gradients from the previous epoch -- `optimizer.zero_grad()` and `model.zero_grad()`
2. Run the model in the forward direction -- `Yhat = model.forward(Xt)`
3. Calculate the loss between our predictions and the truth -- `loss = loss_fn(Yhat,Yt)`
4. Calculate back propagation of the loss through the network -- `loss.backward()`
5. Run the stochastic gradient descent and update the weights -- `optimizer.step()`

Some libraries hide all of these aspects, but PyTorch makes you do them explicitly.  It results in a little more code, but allows for some very fancy models (those involving different losses being calculated independently) to be done with very little change in the code.

#Step 6 -- Training Your Model (20 pts)
* Set up your training method
* Set up your loss function 
* Run the training process as defined above
"""

# Convert our numpy arrays to torch tensors
Xt = torch.Tensor(X).to('cuda')
# To make Yt match the shape of Yhat, we'll need it to be a slightly different shape
Yt = torch.Tensor(Y.reshape((len(Y), 1))).to('cuda')


def train(X: torch.Tensor, Y: torch.Tensor, model: torch.nn.Module, epochs: int) -> None:
    # TODO set the optimizer and loss functions
    optimizer = torch.optim.SGD(model.parameters(), lr=0.01)

    # TODO set the loss function
    # We'll use mean squared error as our loss function
    loss_fn = torch.nn.MSELoss()
    for t in range(epochs):

        # TODO do the training steps here
        # 1. zero the gradient buffers
        optimizer.zero_grad()
        # 1. Clear out the "gradient", i.e. the old update amounts
        model.zero_grad()
        # 2. Make a prediction
        Yhat = model.forward(Xt)
        # 3. Calculate loss (the error of the residual)
        loss = loss_fn(Yhat, Yt)
        if t % 100 == 0:
            print(t, loss.item())

        # 4. Run the loss backwards through the graph
        loss.backward()
        # 5. Run the optimizer to update the weights
        optimizer.step()


train(Xt, Yt, model, 5000)

"""Now we want to see how it did.  We will plot the residuals (i.e. the error) for both our training set and our validation set.  It is always important to have a validation set, as it will let us see how well our model is over (or under) fitting the data."""

Yhat = model.forward(Xt).data.cpu().numpy()

residual = calculate_residuals(Y, Yhat)

plt.plot(Y, residual, 'x')


Yhat_validation = model.forward(torch.Tensor(
    X_validation).to('cuda')).data.cpu().numpy()

residual_validation = calculate_residuals(Y_validation, Yhat_validation)

plt.plot(Y_validation, residual_validation, 'ro')
plt.show()


print('RMSE:', calculate_rmse(residual))
print('Validation RMSE:', calculate_rmse(residual_validation))

"""...And we do just about the same as we did before.

Now let's try it with some hidden layers.  Instead of just 1 Linear layer, we will have multiple layers.  As with the last one, we will have to specify the in_dimensions (identical to that one).  However, instead of an out_dimension of 1, we will go to the number of hidden_units, let's say 100.  Then we will have an output layer, which will go from our hidden_units dimension to an out_dimension of 1.

Again, your model summary should look similar to below (layer weights will be different)

#Step 7 -- Multi Layer Neural Network (10 pts)
* Create a neural network with 1 hidden layer (i.e. 2 layers, Input -> Hidden, Hidden -> Output)
"""

hidden_units = 100
# TODO construct the model
# Define a neural network model as a stack of layers
model = torch.nn.Sequential(
    torch.nn.Linear(X.shape[1], hidden_units, bias=True),
    torch.nn.Linear(hidden_units, 1, bias=True)
)

model.to('cuda')
print(list(model.parameters()))

"""Copy your training code from above and let's see how well it does."""

# Convert our numpy arrays to torch tensors
Xt = torch.Tensor(X).to('cuda')
# To make Yt match the shape of Yhat, we'll need it to be a slightly different shape
Yt = torch.Tensor(Y.reshape((len(Y), 1))).to('cuda')


def train(X: torch.Tensor, Y: torch.Tensor, model: torch.nn.Module, epochs: int) -> None:
    # TODO set the optimizer and loss functions
    optimizer = torch.optim.SGD(model.parameters(), lr=0.01)

    # TODO set the loss function
    # We'll use mean squared error as our loss function
    loss_fn = torch.nn.MSELoss()
    for t in range(epochs):

        # TODO do the training steps here
        # 1. zero the gradient buffers
        optimizer.zero_grad()
        # 1. Clear out the "gradient", i.e. the old update amounts
        model.zero_grad()
        # 2. Make a prediction
        Yhat = model.forward(Xt)
        # 3. Calculate loss (the error of the residual)
        loss = loss_fn(Yhat, Yt)
        if t % 100 == 0:
            print(t, loss.item())

        # 4. Run the loss backwards through the graph
        loss.backward()
        # 5. Run the optimizer to update the weights
        optimizer.step()


train(Xt, Yt, model, 300)

"""Hmmmm.....that's no good. Our loss quickly explodes and goes to nan.  This is cause by our stochastic gradient descent ping-ponging back and forth.  Instead of converging it keeps overshooting more and more until it goes beyond the floating point limit.  Obviously, that isn't what we want.

We can address this in one of 2 ways:

1. We can shrink out learning rate to a small enough value that this no longer occurs
2. We can clip our gradients to make sure they don't exceed a specific value

We can do it the first way, but that will slow our training.  The second can be achieved by adding a step into our training process:


1. Zero the gradients from the previous epoch -- `optimizer.zero_grad()` and `model.zero_grad()`
2. Run the model in the forward direction -- `Yhat = model.forward(Xt)`
3. Calculate the loss between our predictions and the truth -- `loss = loss_fn(Yhat,Yt)`
4. Calculate back propagation of the loss through the network -- `loss.backward()`
5. **Clip the gradients** -- `torch.nn.utils.clip_grad_norm_(model.parameters(),5)`
6. Run the stochastic gradient descent and update the weights -- `optimizer.step()`

Copy your model construction with the hidden layers from above, and then set up an optimization loop with gradient clipping.

#Step 8 -- Gradient Clipping  (10 pts)
* Modify your training method from step 6 to add in Gradient Clipping
"""

hidden_units = 100
# TODO construct the model
# Define a neural network model as a stack of layers
model = torch.nn.Sequential(
    torch.nn.Linear(X.shape[1], hidden_units, bias=True),
    torch.nn.Linear(hidden_units, 1, bias=True)
)

model.to('cuda')


def train_with_gradient_clipping(X: torch.Tensor, Y: torch.Tensor, model: torch.nn.Module, epochs: int) -> None:
    # TODO set the optimizer and loss functions
    optimizer = torch.optim.SGD(model.parameters(), lr=0.01)

    # TODO set the loss function
    # We'll use mean squared error as our loss function
    loss_fn = torch.nn.MSELoss()
    for t in range(epochs):

        # TODO do the training steps here
        # 1. zero the gradient buffers
        optimizer.zero_grad()
        # 1. Clear out the "gradient", i.e. the old update amounts
        model.zero_grad()
        # 2. Make a prediction
        Yhat = model.forward(Xt)
        # 3. Calculate loss (the error of the residual)
        loss = loss_fn(Yhat, Yt)
        if t % 100 == 0:
            print(t, loss.item())

        # 4. Run the loss backwards through the graph
        loss.backward()
        # 5. Clip the gradients
        torch.nn.utils.clip_grad_norm_(model.parameters(), 5)
        # 6. Run the optimizer to update the weights
        optimizer.step()


train_with_gradient_clipping(Xt, Yt, model, 5000)

Yhat = model.forward(Xt).data.cpu().numpy()

residual = calculate_residuals(Y, Yhat)

plt.plot(Y, residual, 'x')


Yhat_validation = model.forward(torch.Tensor(
    X_validation).to('cuda')).data.cpu().numpy()

residual_validation = calculate_residuals(Y_validation, Yhat_validation)

plt.plot(Y_validation, residual_validation, 'ro')
plt.show()


print('RMSE:', calculate_rmse(residual))
print('Validation RMSE:', calculate_rmse(residual_validation))

"""Wait, that looks just like it did before!  The key to neural networks comes from the non-linear activations.  No matter how many layers we add, so long as the rank of the hidden layers is $\geq$ the rank of the original vector, the best we can do is the least squares estimation (as it is the maximum likelihood estimator for a linear regression).  If the rank is decreased, then we are doing some form of compression, akin to Principal Component Analysis.  Let's try it with a bit of nonlinearity. 

Let's do a single hidden layer with a non-linear activation -- we will use the Rectified Linear Unit (ReLU) as it is fast and all we really care about is ANY kind of nonlinearity (sometimes we care about our nonlinearity having a specific meaning or mapping into a specific range (0 to 1, -1 to 1, etc.).

This means we should now have a Sequential model with

1. A Linear layer going from our input dimension to the number of hidden units
2. A ReLU activation layer -- `torch.nn.ReLU()`
3. A Linear layer going from our hidden units to 1


#Step 9 -- Create a non-linear multi layer Neural Network (10 pts)
* Your network should be two layers like above, but should have a non-linear activation function (the ReLU) (e.g.  Input -> Hidden, ReLU, Hidden -> Output)

"""

hidden_units = 100
# TODO construct the model
# Define a neural network model as a stack of layers
model = torch.nn.Sequential(
    torch.nn.Linear(X.shape[1], hidden_units, bias=True),
    torch.nn.ReLU(),
    torch.nn.Linear(hidden_units, 1, bias=True)
)


model.to('cuda')
print(list(model.parameters()))

"""Use the optimization code with the gradient clipping from above to train our new, non-linear, model.  I recommend letting it run for about 10000 epochs.

"""

train_with_gradient_clipping(Xt, Yt, model, 10000)

Yhat = model.forward(Xt).data.cpu().numpy()

residual = calculate_residuals(Y, Yhat)

plt.plot(Y, residual, 'x')


Yhat_validation = model.forward(torch.Tensor(
    X_validation).to('cuda')).data.cpu().numpy()

residual_validation = calculate_residuals(Y_validation, Yhat_validation)

plt.plot(Y_validation, residual_validation, 'ro')
plt.show()


print('RMSE:', calculate_rmse(residual))
print('Validation RMSE:', calculate_rmse(residual_validation))

"""Ah, that looks better.  Note, you are probably overfitting (it is the tendency of these techniques), you can try some form of regularization (e.g., dropout) to reduce this overfitting for extra-credit.  

You can try to explore different network topologies (different numbers of layers, different activation functions) and different training techniques to see how well you can do on the validation set.

Now, let's use this as a heuristic for our search.

Below are the helper functions needed -- use them in your A* implementation

#BONUS -- A* (15 pts)
* Implement A* search for the MineCraft planning domain, using the above estimates as  heuristics
"""


with open('Crafting.json') as f:
    Crafting = json.load(f)
items_by_index = list(sorted(Crafting['Items']))
items_to_indices = {item: index for index, item in enumerate(items_by_index)}


class State:

    def __init__(self, items=None):
        if items is not None:
            # Copying a state from an old state.
            # This call to the array constructor creates an array of unsigned integers and initializes it from the contents of items.
            self.items = array.array('I', items)
        else:
            self.items = array.array('I', [0 for item in items_by_index])

    def __add__(self, other):
        s = State(self.items)
        # A. How do we add together the contents of two states?
        for ii, oi in enumerate(other.items):
            s.items[ii] += oi
        return s

    def __sub__(self, other):
        s = State(self.items)
        # A. How do we add together the contents of two states?
        for ii, oi in enumerate(other.items):
            s.items[ii] -= oi
        return s

    def __ge__(self, other):
        # C. How do we know whether one state (self) contains everything that's inside of another (other)?
        for si, oi in zip(self.items, other.items):
            if si < oi:
                return False
        return True

    def __lt__(self, other):
        return not (self >= other)

    def __eq__(self, other):
        return self.items == other.items

    def __hash__(self):
        hsh = 5381
        for s in self.items:
            hsh = ((hsh << 5) + hsh) + s
        return hsh

    def __str__(self):
        out_str = []
        for k, v in self.to_dict().items():
            out_str.append('{}:{}'.format(k, v))
        return ','.join(out_str)

    def to_dict(self):
        return {items_by_index[idx]: self.items[idx]
                for idx in range(len(self.items))}

    @classmethod
    def from_dict(cls, item_dict: Dict[str, int]) -> 'State':
        return cls([
            item_dict.get(item, 0) for item in items_by_index
        ])


class Recipe(NamedTuple):
    produces: State
    consumes: State
    requires: State
    cost: int


recipes: Dict[str, Recipe] = {}
for name, rule in Crafting['Recipes'].items():
    recipes[name] = Recipe(
        State.from_dict(rule.get('Produces', {})),
        State.from_dict(rule.get('Consumes', {})),
        State.from_dict({item: 1 if req else 0
                         for item, req in rule.get('Requires', {}).items()}),
        rule['Time']
    )


def preconditions_satisfied(state: State, recipe: Recipe) -> bool:
    return state >= recipe.consumes and state >= recipe.requires


def apply_effects(state: State, recipe: Recipe) -> State:
    return state-recipe.consumes+recipe.produces


def states_to_tensor(initial_state: State, goal_state: State) -> torch.Tensor:
    items = ['bench', 'cart', 'coal', 'cobble',
             'furnace', 'ingot', 'iron_axe',
             'iron_pickaxe', 'ore', 'plank', 'rail',
             'stick', 'stone_axe', 'stone_pickaxe',
             'wood', 'wooden_axe', 'wooden_pickaxe']
    data = []
    initial_state = initial_state.to_dict()
    goal_state = goal_state.to_dict()
    for i in items:
        data.append([initial_state[i]])
    for i in items:
        data.append([goal_state[i]])
    return torch.Tensor(np.array(data).T)


def get_heuristic(current_state: State, goal_state: State) -> float:
    return model.forward(states_to_tensor(current_state, goal_state)).data.numpy()[0, 0]


pruning = [State.from_dict({'cobble': 9}),
           State.from_dict({'wood': 3}),
           State.from_dict({'plank': 9}),
           State.from_dict({'ore': 2}),
           State.from_dict({'stick': 6}),
           State.from_dict({'bench': 2}),
           State.from_dict({'furnace': 2}),
           State.from_dict({'iron_axe': 2}),
           State.from_dict({'iron_pickaxe': 2}),
           State.from_dict({'stone_axe': 2}),
           State.from_dict({'stone_pickaxe': 2}),
           State.from_dict({'wooden_axe': 2}),
           State.from_dict({'wooden_pickaxe': 2}),
           State.from_dict({'coal': 2})]


def prune(state: State) -> bool:
    to_prune = False
    for p in pruning:
        if state >= p:
            to_prune = True
            break

    return to_prune

# TODO implement A* search
# It should return a tuple of the number of states visited, the time cost,
# and the path of recipes it takes (as a list of recipe names)
# Break the loop when you have visited max_nodes
# I recommend using the above prune method after applying a recipe
# but before adding a node to the open set


def a_star(initial: State, goal: State, max_nodes: int) -> Tuple[int, int, Optional[List[str]]]:
    pass


print(a_star(State.from_dict({'wood': 1}),
             State.from_dict({'wooden_pickaxe': 1}), 1000))
print(a_star(State.from_dict({'wood': 1}),
             State.from_dict({'iron_pickaxe': 1}), 20000))
print(a_star(State.from_dict({}), State.from_dict({'rail': 1}), 20000))
print(a_star(State.from_dict({}), State.from_dict({'cart': 1}), 20000))
