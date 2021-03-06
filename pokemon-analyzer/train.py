import numpy as np
import parser as parser
import tensorflow as tf
import json



def main():

    # Validation parameters
    folds = 5

    ###########################################
    ###########################################
    ###########################################

    teams_dataset = parser.parseTeams()

    data_x, data_y = transform_teams(teams_dataset)

    # We shuffle training data randomly
    p = np.random.permutation(len(data_x))
    data_x, data_y = data_x[p], data_y[p]

    train_x, train_y = data_x[:-len(data_x)/folds], data_y[:-len(data_x)/folds]
    test_x, test_y = data_x[-len(data_x)/folds:], data_y[-len(data_x)/folds:]

    print ("Training shape: "+str(np.shape(train_x)) + ", "+str(np.shape(train_y)))
    print ("Testing shape: "+str(np.shape(test_x)) + ", "+str(np.shape(test_y)))

    ###########################################
    ###########################################
    ###########################################

    # Parameters
    learning_rate = 0.001
    training_epochs = 300
    batch_size = 100
    display_step = 1

    # Network Parameters
    n_hidden_1 = 256  # 1st layer number of neurons
    n_hidden_2 = 256  # 2nd layer number of neurons
    n_hidden_3 = 256  # 2nd layer number of neurons
    n_input = 950  # MNIST data input (img shape: 28*28)
    n_classes = 742  # MNIST total classes (0-9 digits)
    #    n_input = 784  # MNIST data input (img shape: 28*28)
    #    n_classes = 10  # MNIST total classes (0-9 digits)

    # tf Graph input
    X = tf.placeholder("float", [None, n_input])
    Y = tf.placeholder("float", [None, n_classes])

    # Store layers weight & bias
    weights = {
        'h1': tf.Variable(tf.random_normal([n_input, n_hidden_1])),
        'h2': tf.Variable(tf.random_normal([n_hidden_1, n_hidden_2])),
        'h3': tf.Variable(tf.random_normal([n_hidden_1, n_hidden_3])),
        'out': tf.Variable(tf.random_normal([n_hidden_2, n_classes]))
    }
    biases = {
        'b1': tf.Variable(tf.random_normal([n_hidden_1])),
        'b2': tf.Variable(tf.random_normal([n_hidden_2])),
        'b3': tf.Variable(tf.random_normal([n_hidden_3])),
        'out': tf.Variable(tf.random_normal([n_classes]))
    }

    # Create model
    def multilayer_perceptron(x):
        # Hidden fully connected layer with 256 neurons
        layer_1 = tf.add(tf.matmul(x, weights['h1']), biases['b1'])
        # Hidden fully connected layer with 256 neurons
        layer_2 = tf.add(tf.matmul(layer_1, weights['h2']), biases['b2'])
        # Hidden fully connected layer with 256 neurons
        layer_3 = tf.add(tf.matmul(layer_2, weights['h3']), biases['b3'])
        # Output fully connected layer with a neuron for each class
        out_layer = tf.matmul(layer_3, weights['out']) + biases['out']
        return out_layer

    # Construct model
    logits = multilayer_perceptron(X)

    # Define loss and optimizer
    loss_op = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits_v2(
        logits=logits, labels=Y))
    optimizer = tf.train.AdamOptimizer(learning_rate=learning_rate)
    train_op = optimizer.minimize(loss_op)
    # Initializing the variables
    init = tf.global_variables_initializer()

    with tf.Session() as sess:
        sess.run(init)

        # Training cycle
        for epoch in range(training_epochs):
            avg_cost = 0.
            total_batch = int(len(train_x) / batch_size)
            # Loop over all batches
            for i in range(total_batch):

                batch_x = train_x[(i*batch_size):((i+1)*batch_size)]
                batch_y = train_y[(i*batch_size):((i+1)*batch_size)]

              #  batch_x, batch_y = mnist.train.next_batch(batch_size)
                # Run optimization op (backprop) and cost op (to get loss value)
                _, c = sess.run([train_op, loss_op], feed_dict={X: batch_x,
                                                                Y: batch_y})
                # Compute average loss
                avg_cost += c / total_batch
            # Display logs per epoch step
            if epoch % display_step == 0:
                print("Epoch:", '%04d' % (epoch + 1), "cost={:.9f}".format(avg_cost))
        print("Optimization Finished!")

        # Test model
        pred = tf.nn.softmax(logits)  # Apply softmax to logits
        correct_prediction = tf.equal(tf.argmax(pred, 1), tf.argmax(Y, 1))
        # Calculate accuracy
        accuracy = tf.reduce_mean(tf.cast(correct_prediction, "float"))
#        print("Accuracy:", accuracy.eval({X: mnist.test.images, Y: mnist.test.labels}))
        print("Accuracy:", accuracy.eval({X: test_x, Y: test_y}))


# We want to transforms the teams set of data into usable trainable data
def transform_teams(teams):
    pass
    # This is a classification problem
    # We will pick the 4 most likely LEGAL moves from the information we know (we filter out unlearnable moves)

    # The y data will be its classification
    # The x data will be:

    # - This Pokemon's species (important as not everything can learn everything)
    # - The types of other moves in the set
    # - The total power of other moves this pokemon has
    # - The total positive priority of moves this pokemon has
    #           (do not include negative ones like Roar, or overly positive ones like Protect)
    # - This Pokemon's type
    # - This Pokemon's base stats
    # - This Pokemon's IVs
    # - This Pokemon's EVs (can infer these from damage calcs)
    # - This Pokemon's Nature (can infer this from damage calcs)
    # - Maybe this Pokemon's items too?

    # - Other Pokemon's types
    # - Other Pokemon's move's types
    # - Other Pokemon's moves total power
    # - Total of non-zero priority moves other Pokemon have
    # - Maybe other Pokemon's items too

    moveFile = open("../pokemon-data/data/moves.json", "r")
    moveJSON = json.load(moveFile)

    pkmnFile = open("../pokemon-data/data/pokedex.json", "r")
    pkmnJson = json.load(pkmnFile)

    types = ["Normal", "Fighting", "Flying", "Poison", "Ground", "Rock", "Bug", "Ghost", "Steel", "Fire", "Water",
             "Grass", "Electric", "Psychic", "Ice", "Dragon", "Dark", "Fairy"]
    natures = ["Hardy", "Lonely", "Brave", "Adamant", "Naughty", "Bold", "Docile", "Relaxed", "Impish", "Lax", "Timid",
               "Hasty", "Serious", "Jolly", "Naive", "Modest", "Mild", "Quiet", "Bashful", "Rash",
               "Calm", "Gentle", "Sassy", "Careful", "Quirky"]

    X = np.zeros(shape=(1,950))
    Y = np.zeros(shape=(1,742))

    for team in teams:
        for pkmn in team:
            moves = np.zeros(shape=(len(pkmn["Moves"]), 950))
            movesY = np.zeros(shape=(len(pkmn["Moves"]), 742))

            for i, move in enumerate(pkmn["Moves"]):

                movesY[i][int(moveJSON[move]["num"])] = 1

                pos = 0
                # 0 0 0 0 0 1 0 0 0
                # Sets 1-hot for this Pokemon's species
                moves[i][pos + pkmnJson[pkmn["Species"]]["num"]] = 1
                pos += pkmnJson["Melmetal"]["num"] # Melmetal is last Pokemon in the Pokedex

                # 0 0 0 1 0 1 0 0 0
                # Sets 1-hots for each of this Pokemon's types (2-hots, I guess?)
                for type_sub in pkmnJson[pkmn["Species"]]["types"]:
                    moves[i][pos + types.index(type_sub)] = 1
                pos += len(types)

                # 0 0 0 0 0 0 1 0 0 0 0 2 0 0 0
                # Sets variables for the types of other moves this Pokemon has.
                # If there are two other Fire-type, there will be a 2 in that moves position.
                # Gives an integer of the move's type
                for j, move_sub in enumerate(pkmn["Moves"]):
                    if i == j:
                        continue
                    moveType = types.index(moveJSON[move]["type"])
                    moves[i][pos + moveType] += 1
                pos += len(types)

                # Sets the total base power of other moves this pokemon has
                totalBP = 0
                for j, move_sub in enumerate(pkmn["Moves"]):
                    if i == j:
                        continue
                    totalBP += moveJSON[move_sub]["basePower"]
                moves[i][pos] = totalBP
                pos += 1

                # Sets the total priority of other moves this pokemon has
                # (priority is only added if it is 1 or 2, to ignore Roar and Protect-likes)
                totalPriority = 0
                for j, move_sub in enumerate(pkmn["Moves"]):
                    if i == j:
                        continue
                    totalPriority += max(0,min(moveJSON[move_sub]["priority"],3))
                moves[i][pos] = totalPriority
                pos += 1

                # Sets the BST of this Pokemon
                moves[i][pos] = pkmnJson[pkmn["Species"]]["baseStats"]["hp"]; pos += 1
                moves[i][pos] = pkmnJson[pkmn["Species"]]["baseStats"]["atk"]; pos += 1
                moves[i][pos] = pkmnJson[pkmn["Species"]]["baseStats"]["def"]; pos += 1
                moves[i][pos] = pkmnJson[pkmn["Species"]]["baseStats"]["spa"]; pos += 1
                moves[i][pos] = pkmnJson[pkmn["Species"]]["baseStats"]["spd"]; pos += 1
                moves[i][pos] = pkmnJson[pkmn["Species"]]["baseStats"]["spe"]; pos += 1

                # Sets the IVs of this Pokemon
                moves[i][pos] = pkmn["iv_HP"]; pos += 1
                moves[i][pos] = pkmn["iv_Atk"]; pos += 1
                moves[i][pos] = pkmn["iv_Def"]; pos += 1
                moves[i][pos] = pkmn["iv_SpA"]; pos += 1
                moves[i][pos] = pkmn["iv_SpD"]; pos += 1
                moves[i][pos] = pkmn["iv_Spe"]; pos += 1

                # Sets the EVs of this Pokemon
                moves[i][pos] = pkmn["ev_HP"]; pos += 1
                moves[i][pos] = pkmn["ev_Atk"]; pos += 1
                moves[i][pos] = pkmn["ev_Def"]; pos += 1
                moves[i][pos] = pkmn["ev_SpA"]; pos += 1
                moves[i][pos] = pkmn["ev_SpD"]; pos += 1
                moves[i][pos] = pkmn["ev_Spe"]; pos += 1

                # Sets this Pokemon's nature
                moves[i][pos + natures.index(pkmn["Nature"])] = 1
                pos += natures.index("Quirky")

                # Set types of other Pokemon and their moves
                for pkmn_sub in team:
                    sub_pos = 0

                    # 0 0 0 1 0 1 0 0 0
                    # Sets 1-hots for each of this Pokemon's types (2-hots, I guess?)
                    for type_sub in pkmnJson[pkmn_sub["Species"]]["types"]:
                        moves[i][pos + sub_pos + types.index(type_sub)] = 1
                    sub_pos += len(types)

                    for move_sub in pkmn_sub["Moves"]:
                        # 0 0 0 1 0 1 0 0 0
                        # Sets 1-hots for each of this Pokemon's moves types (2-hots, I guess?)
                        moves[i][pos + sub_pos + types.index(moveJSON[move_sub]["type"])] = 1
                    sub_pos += len(types)
                pos += 2 * len(types)

            X = np.concatenate((X, moves))
            Y = np.concatenate((Y, movesY))
    # todo: only 7 lines apparently?
    return X, Y


if __name__ == "__main__":
    main()