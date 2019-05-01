import numpy as np
import parser as parser
import tensorflow as tf
import json


def main():

    learning_rate = 0.01
    training_iteration = 30
    batch_size = 100
    display_step = 2

    teams_dataset = parser.parseTeams()
    train_x, train_y = transform_teams(teams_dataset)
    test_x, test_y = train_x, train_y

    print ("SEE SIZES")
    print (np.shape(train_x))
    print (np.shape(train_y))
    print (np.shape(test_x))
    print (np.shape(test_y))

    print("starting tensorflow...")

    tf_x = tf.placeholder("float", [None, 950])
    tf_y = tf.placeholder("float", [None, 742])

    W = tf.Variable(tf.zeros([950,742]))
    b = tf.Variable(tf.zeros([742]))

    with tf.name_scope("Wx_b") as scope:
        # constructs linear model
        model = tf.nn.softmax(tf.matmul(tf_x, W) + b)

    w_h = tf.summary.histogram("weights",W)
    w_h = tf.summary.histogram("biases",b)

    with tf.name_scope("cost_function") as scope:
        # minimize error using entropy
        cost_function = -tf.reduce_sum(tf_y*tf.log(model))
        # create summary to monitor it
        tf.summary.scalar("cost_function", cost_function)

    with tf.name_scope("train") as scope:
        # Gradient descent
        optimizer = tf.train.GradientDescentOptimizer(learning_rate).minimize(cost_function)

    init = tf.initialize_all_variables()

    merged_summary_op = tf.summary.merge_all()

    #Launch graph
    with tf.Session() as sess:
        sess.run(init)

        summary_writer = tf.summary.FileWriter('/tmp/tensorflow_logs',graph_def=sess.graph_def)

        # Training cycle
        for iteration in range(training_iteration):
            avg_cost = 0
            total_batch = int(len(train_x)/batch_size)
            # loops over batches
            for i in range(total_batch):
                batch_xs = train_x[i*batch_size:(i+1)*batch_size - 1,:]
                batch_ys = train_y[i*batch_size:(i+1)*batch_size - 1,:]
                # fit training using batch data
                sess.run(optimizer,feed_dict={tf_x: batch_xs, tf_y: batch_ys})
                # Compute average loss
                avg_cost += sess.run(cost_function, feed_dict={tf_x: batch_xs, tf_y:batch_ys})/total_batch
                # write logs
                summary_str = sess.run(merged_summary_op, feed_dict={tf_x: batch_xs, tf_y:batch_ys})
                summary_writer.add_summary(summary_str,iteration*total_batch + i)
            # Displays log per iteration step
            if iteration % display_step == 0:
                print "Iteration:", '%04d' % (iteration +1), "cost=","{:.9f}".format(avg_cost)
        # Test
        predictions = tf.equal(tf.argmax(model,1),tf.argmax(tf_y,1))
        # Calculate accuracy
        accuracy = tf.reduce_mean(tf.cast(predictions,"float"))
        print "Accuracy: "+accuracy.eval({tf_x: test_x, tf_y: test_y})

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

    X = np.zeros(shape=(950,1))
    Y = np.zeros(shape=(950,1))

    for team in teams:
        for pkmn in team:

            moves = np.zeros(shape=(len(pkmn["Moves"]), 950))
            movesY = np.zeros(shape=(len(pkmn["Moves"]), 1))

            for i, move in enumerate(pkmn["Moves"]):

                movesY[i] = moveJSON[move]["num"]

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

            np.append(X, moves)
            np.append(Y, movesY)
    return X, Y


if __name__ == "__main__":
    main()