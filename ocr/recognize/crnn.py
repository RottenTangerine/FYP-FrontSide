import torch.nn as nn
from collections import OrderedDict


class BidirectionalLSTM(nn.Module):

    def __init__(self, nIn, nHidden, nOut):
        super(BidirectionalLSTM, self).__init__()

        self.rnn = nn.LSTM(nIn, nHidden, bidirectional=True)
        self.embedding = nn.Linear(nHidden * 2, nOut)

    def forward(self, input):
        recurrent, _ = self.rnn(input)
        T, b, h = recurrent.size()
        t_rec = recurrent.view(T * b, h)

        output = self.embedding(t_rec)  # [T * b, nOut]
        output = output.view(T, b, -1)
        return output


class CRNN(nn.Module):

    def __init__(self, imgH, nc, nclass, nh, leakyRelu=False):
        super(CRNN, self).__init__()
        assert imgH % 16 == 0, 'imgH has to be a multiple of 16'

        # 1x32x128
        self.conv1 = nn.Conv2d(nc, 64, 3, 1, 1)
        self.relu1 = nn.ReLU(True)
        self.pool1 = nn.MaxPool2d(2, 2)

        # 64x16x64
        self.conv2 = nn.Conv2d(64, 128, 3, 1, 1)
        self.relu2 = nn.ReLU(True)
        self.pool2 = nn.MaxPool2d(2, 2)

        # 128x8x32
        self.conv3_1 = nn.Conv2d(128, 256, 3, 1, 1)
        self.bn3 = nn.BatchNorm2d(256)
        self.relu3_1 = nn.ReLU(True)
        self.conv3_2 = nn.Conv2d(256, 256, 3, 1, 1)
        self.relu3_2 = nn.ReLU(True)
        self.pool3 = nn.MaxPool2d((2, 2), (2, 1), (0, 1))

        # 256x4x16
        self.conv4_1 = nn.Conv2d(256, 512, 3, 1, 1)
        self.bn4 = nn.BatchNorm2d(512)
        self.relu4_1 = nn.ReLU(True)
        self.conv4_2 = nn.Conv2d(512, 512, 3, 1, 1)
        self.relu4_2 = nn.ReLU(True)
        self.pool4 = nn.MaxPool2d((2, 2), (2, 1), (0, 1))

        # 512x2x16
        self.conv5 = nn.Conv2d(512, 512, 2, 1, 0)
        self.bn5 = nn.BatchNorm2d(512)
        self.relu5 = nn.ReLU(True)

        # 512x1x16

        self.rnn = nn.Sequential(
            BidirectionalLSTM(512, nh, nh),
            BidirectionalLSTM(nh, nh, nclass))

    def forward(self, input):
        # conv features
        x = self.pool1(self.relu1(self.conv1(input)))
        x = self.pool2(self.relu2(self.conv2(x)))
        x = self.pool3(self.relu3_2(self.conv3_2(self.relu3_1(self.bn3(self.conv3_1(x))))))
        x = self.pool4(self.relu4_2(self.conv4_2(self.relu4_1(self.bn4(self.conv4_1(x))))))
        conv = self.relu5(self.bn5(self.conv5(x)))
        # print(conv.size())

        b, c, h, w = conv.size()
        assert h == 1, "the height of conv must be 1"
        conv = conv.squeeze(2)
        conv = conv.permute(2, 0, 1)  # [w, b, c]

        # rnn features
        output = self.rnn(conv)

        return output


class CRNN_v2(nn.Module):

    def __init__(self, imgH, nc, nclass, nh, leakyRelu=False):
        super(CRNN_v2, self).__init__()
        assert imgH % 16 == 0, 'imgH has to be a multiple of 16'

        # 1x32x128
        self.conv1_1 = nn.Conv2d(nc, 32, 3, 1, 1)
        self.bn1_1 = nn.BatchNorm2d(32)
        self.relu1_1 = nn.ReLU(True)

        self.conv1_2 = nn.Conv2d(32, 64, 3, 1, 1)
        self.bn1_2 = nn.BatchNorm2d(64)
        self.relu1_2 = nn.ReLU(True)
        self.pool1 = nn.MaxPool2d(2, 2)

        # 64x16x64
        self.conv2_1 = nn.Conv2d(64, 64, 3, 1, 1)
        self.bn2_1 = nn.BatchNorm2d(64)
        self.relu2_1 = nn.ReLU(True)

        self.conv2_2 = nn.Conv2d(64, 128, 3, 1, 1)
        self.bn2_2 = nn.BatchNorm2d(128)
        self.relu2_2 = nn.ReLU(True)
        self.pool2 = nn.MaxPool2d(2, 2)

        # 128x8x32
        self.conv3_1 = nn.Conv2d(128, 96, 3, 1, 1)
        self.bn3_1 = nn.BatchNorm2d(96)
        self.relu3_1 = nn.ReLU(True)

        self.conv3_2 = nn.Conv2d(96, 192, 3, 1, 1)
        self.bn3_2 = nn.BatchNorm2d(192)
        self.relu3_2 = nn.ReLU(True)
        self.pool3 = nn.MaxPool2d((2, 2), (2, 1), (0, 1))

        # 192x4x32
        self.conv4_1 = nn.Conv2d(192, 128, 3, 1, 1)
        self.bn4_1 = nn.BatchNorm2d(128)
        self.relu4_1 = nn.ReLU(True)
        self.conv4_2 = nn.Conv2d(128, 256, 3, 1, 1)
        self.bn4_2 = nn.BatchNorm2d(256)
        self.relu4_2 = nn.ReLU(True)
        self.pool4 = nn.MaxPool2d((2, 2), (2, 1), (0, 1))

        # 256x2x32
        self.bn5 = nn.BatchNorm2d(256)

        # 256x2x32

        self.rnn = nn.Sequential(
            BidirectionalLSTM(512, nh, nh),
            BidirectionalLSTM(nh, nh, nclass))

    def forward(self, input):
        # conv features
        x = self.pool1(self.relu1_2(self.bn1_2(self.conv1_2(self.relu1_1(self.bn1_1(self.conv1_1(input)))))))
        x = self.pool2(self.relu2_2(self.bn2_2(self.conv2_2(self.relu2_1(self.bn2_1(self.conv2_1(x)))))))
        x = self.pool3(self.relu3_2(self.bn3_2(self.conv3_2(self.relu3_1(self.bn3_1(self.conv3_1(x)))))))
        x = self.pool4(self.relu4_2(self.bn4_2(self.conv4_2(self.relu4_1(self.bn4_1(self.conv4_1(x)))))))
        conv = self.bn5(x)
        # print(conv.size())

        b, c, h, w = conv.size()
        assert h == 2, "the height of conv must be 2"
        conv = conv.reshape([b, c * h, w])
        conv = conv.permute(2, 0, 1)  # [w, b, c]

        # rnn features
        output = self.rnn(conv)

        return output


def conv3x3(nIn, nOut, stride=1):
    # "3x3 convolution with padding"
    return nn.Conv2d(nIn, nOut, kernel_size=3, stride=stride, padding=1, bias=False)


class BasicResidualBlock(nn.Module):

    def __init__(self, in_channels, out_channels, stride=1, shortcut=None):
        super(BasicResidualBlock, self).__init__()
        self.conv = nn.Sequential(
            nn.Conv2d(in_channels, out_channels, kernel_size=3, stride=stride, padding=1, bias=False),
            nn.InstanceNorm2d(out_channels),
            nn.LeakyReLU(0.1, inplace=True),
            nn.Conv2d(out_channels, out_channels, kernel_size=3, stride=1, padding=1, bias=False),
            nn.InstanceNorm2d(out_channels),
        )

        self.leaky_relu = nn.Sequential(nn.LeakyReLU(0.1, inplace=True))

        self.shortcut = nn.Sequential()
        if shortcut:
            self.shortcut = shortcut

    def forward(self, x):
        out = self.conv(x) + self.shortcut(x)
        out = self.leaky_relu(out)
        return out


class CRNN_res(nn.Module):

    def __init__(self, imgH, nc, nclass, nh):
        super(CRNN_res, self).__init__()
        assert imgH % 16 == 0, 'imgH has to be a multiple of 16'

        self.conv1 = nn.Conv2d(nc, 64, 3, 1, 1)
        self.leaky_relu1 = nn.LeakyReLU(0.1, True)
        self.res1 = BasicResidualBlock(64, 64)
        # [C, H] = 64 x 32

        short_cut1 = nn.Sequential(nn.Conv2d(64, 128, kernel_size=1, stride=2, bias=False), nn.InstanceNorm2d(128))
        self.res2_1 = BasicResidualBlock(64, 128, stride=2, shortcut=short_cut1)
        self.res2_2 = BasicResidualBlock(128, 128)
        # [C, H] = 128 x 16; w = w / 2

        short_cut2 = nn.Sequential(nn.Conv2d(128, 256, kernel_size=1, stride=2, bias=False), nn.InstanceNorm2d(256))
        self.res3_1 = BasicResidualBlock(128, 256, stride=2, shortcut=short_cut2)
        self.res3_2 = BasicResidualBlock(256, 256)
        self.res3_3 = BasicResidualBlock(256, 256)
        # [C, H] = 256 x 8; w = w / 2

        short_cut3 = nn.Sequential(nn.Conv2d(256, 512, kernel_size=1, stride=(2, 1), bias=False), nn.InstanceNorm2d(512))
        self.res4_1 = BasicResidualBlock(256, 512,  stride=(2, 1), shortcut=short_cut3)
        self.res4_2 = BasicResidualBlock(512, 512)
        self.res4_3 = BasicResidualBlock(512, 512)
        # [C, H] = 512 x 4; w = w

        self.pool = nn.AvgPool2d((2, 2), (2, 1), (0, 1))
        # [C, H] = 512 x 2; w = w

        self.conv5 = nn.Conv2d(512, 512, 2, 1, 0)
        self.bn5 = nn.InstanceNorm2d(512)
        self.leaky_relu5 = nn.LeakyReLU(True)
        # [C, H] = 512 x 1; w = w

        self.rnn = nn.Sequential(
            BidirectionalLSTM(512, nh, nh),
            BidirectionalLSTM(nh, nh, nclass))

    def forward(self, input):
        # conv features
        x = self.res1(self.leaky_relu1(self.conv1(input)))  # 64 x 32 x w
        x = self.res2_2(self.res2_1(x))  # 128 x 16 x w
        x = self.res3_3(self.res3_2(self.res3_1(x)))  # 256 x 8 x w
        x = self.res4_3(self.res4_2(self.res4_1(x)))  # 512 x 4 x w
        x = self.pool(x)  # 512 x 2 x w
        conv = self.leaky_relu5(self.bn5(self.conv5(x)))  # 512 x 1 x w
        b, c, h, w = conv.size()
        assert h == 1, "the height of conv must be 1"
        conv = conv.squeeze(2)
        conv = conv.permute(2, 0, 1)  # [w, b, c]

        # rnn features
        output = self.rnn(conv)

        return output





if __name__ == '__main__':
    pass
