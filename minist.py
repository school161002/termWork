import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ["PATH"] += os.pathsep + 'C:/Program Files (x86)/Graphviz2.38/bin/'
from tensorflow.keras.utils import plot_model
from tensorflow.keras.callbacks import ReduceLROnPlateau
from tensorflow.keras.layers import MaxPool2D
from tensorflow.keras.layers import Flatten
from tensorflow.keras.layers import Conv2D
from tensorflow.keras.layers import Dense
from tensorflow.keras.layers import Input
from tensorflow.keras.models import Model
from sklearn.model_selection import train_test_split
import numpy as np
import random
import matplotlib.pyplot as plt
import tensorflow as tf


def evaluate(model):
    # 按照错一个就算错的规则计算准确率.
    result = model.evaluate(np.array(X_test).reshape(len(X_test), 28, 140, 1), [
                            y_test[0], y_test[1], y_test[2], y_test[3], y_test[4]], batch_size=32)
    return result[6] * result[7] * result[8] * result[9] * result[10]


def get_result(result):
    # 将 one_hot 编码解码
    resultstr = ''
    for i in range(n_len):
        resultstr += str(np.argmax(result[i])) + ','
    return resultstr


def generate_dataset(X, y):
    X_len = X.shape[0]  # 原数据集有几个，新数据集还要有几个
    # 新数据集的shape为(X_len, 28, 28*5, 1)，X_len是X的个数，原数据集是28x28，取5个数字(包含空白)拼接，则为28x140, 1是颜色通道，灰度图，所以是1
    X_gen = np.zeros((X_len, height, width*n_len, 1), dtype=np.uint8)
    # 新数据集对应的label，最终的shape为（5,  X_len，11）
    y_gen = [np.zeros((X_len, n_class), dtype=np.uint8) for i in range(n_len)]

    for i in range(X_len):
        # 随机确定数字长度
        rand_len = random.randint(1, 5)
        lis = list()
        # 设置每个数字
        for j in range(0, rand_len):
            # 随机找一个数
            index = random.randint(0, X_len - 1)
            # 将对应的y置1, y是经过onehot编码的，所以y的第三维是11，0~9为10个数字，10为空白，哪个索引为1就是数字几
            y_gen[j][i][y[index]] = 1
            lis.append(X[index].T)
        # 其余位取空白
        for m in range(rand_len, 5):
            # 将对应的y置1
            y_gen[m][i][10] = 1
            lis.append(np.zeros((28, 28), dtype=np.uint8))
        lis = np.array(lis).reshape(140, 28).T
        X_gen[i] = lis.reshape(28, 140, 1)
    return X_gen, y_gen


mnist = tf.keras.datasets.mnist
(X_raw, y_raw), (X_raw_test, y_raw_test) = mnist.load_data()
n_train, n_test = X_raw.shape[0], X_raw_test.shape[0]

n_class, n_len, width, height = 11, 5, 28, 28
X_raw_train, X_raw_valid, y_raw_train, y_raw_valid = train_test_split(
    X_raw, y_raw, test_size=0.2, random_state=50)
X_train, y_train = generate_dataset(X_raw_train, y_raw_train)
X_valid, y_valid = generate_dataset(X_raw_valid, y_raw_valid)
X_test, y_test = generate_dataset(X_raw_test, y_raw_test)

# 查看数据集
# for i in range(15):
#     plt.subplot(3, 5, i+1)
#     index = random.randint(0, n_train-1)
#     plt.title(str(y_raw[index]))
#     plt.imshow(X_raw[index], cmap='gray')
#     plt.axis('off')
# plt.show()
for i in range(15):
    plt.subplot(5, 3, i+1)
    index = random.randint(0, n_test-1)
    title = ''
    for j in range(n_len):
        title += str(np.argmax(y_test[j][index])) + ','
    plt.title(title)
    plt.imshow(X_test[index][:, :, 0], cmap='gray')
    plt.axis('off')
plt.show()
# 尝试加载已保存的训练好的模型,如果没有则训练一个模型
try:
    model = tf.keras.models.load_model('model.h5')
except BaseException:
    inputs = Input(shape=(28, 140, 1))
    conv_11 = Conv2D(filters=32, kernel_size=(
        5, 5), padding='Same', activation='relu')(inputs)
    max_pool_11 = MaxPool2D(pool_size=(2, 2))(conv_11)
    conv_12 = Conv2D(filters=10, kernel_size=(
        3, 3), padding='Same', activation='relu')(max_pool_11)
    max_pool_12 = MaxPool2D(pool_size=(2, 2), strides=(2, 2))(conv_12)
    flatten11 = Flatten()(max_pool_12)
    hidden11 = Dense(15, activation='relu')(flatten11)
    prediction1 = Dense(11, activation='softmax')(hidden11)
    hidden21 = Dense(15, activation='relu')(flatten11)
    prediction2 = Dense(11, activation='softmax')(hidden21)
    hidden31 = Dense(15, activation='relu')(flatten11)
    prediction3 = Dense(11, activation='softmax')(hidden31)
    hidden41 = Dense(15, activation='relu')(flatten11)
    prediction4 = Dense(11, activation='softmax')(hidden41)
    hidden51 = Dense(15, activation='relu')(flatten11)
    prediction5 = Dense(11, activation='softmax')(hidden51)
    model = Model(inputs=inputs, outputs=[
                  prediction1, prediction2, prediction3, prediction4, prediction5])

    learnrate_reduce_1 = ReduceLROnPlateau(
        monitor='val_dense_1_accuracy', patience=2, verbose=1, factor=0.8, min_lr=0.00001)
    learnrate_reduce_2 = ReduceLROnPlateau(
        monitor='val_dense_3_accuracy', patience=2, verbose=1, factor=0.8, min_lr=0.00001)
    learnrate_reduce_3 = ReduceLROnPlateau(
        monitor='val_dense_5_accuracy', patience=2, verbose=1, factor=0.8, min_lr=0.00001)
    learnrate_reduce_4 = ReduceLROnPlateau(
        monitor='val_dense_7_accuracy', patience=2, verbose=1, factor=0.8, min_lr=0.00001)
    learnrate_reduce_5 = ReduceLROnPlateau(
        monitor='val_dense_9_accuracy', patience=2, verbose=1, factor=0.8, min_lr=0.00001)

    model.compile(optimizer='rmsprop',
                  loss='categorical_crossentropy',
                  metrics=['accuracy'])
    model.fit(X_train, y_train, epochs=20, batch_size=128,
              validation_data=(X_valid, y_valid),
              callbacks=[learnrate_reduce_1, learnrate_reduce_2, learnrate_reduce_3, learnrate_reduce_4, learnrate_reduce_5], verbose=2)
    # 保存模型
    model.save('model.h5')
    # 模型可视化为图片
    plot_model(model, to_file='model.png')

model.summary()
print(evaluate(model))
# 预测值可视化
index = random.randint(0, n_test-1)
y_pred = model.predict(X_test[index].reshape(1, 28, 140, 1))
plt.title('real: %s\npred:%s' % (get_result(
    [y_test[x][index] for x in range(n_len)]), get_result(y_pred)))
plt.imshow(X_test[index, :, :, 0], cmap='gray')
plt.axis('off')
plt.show()
