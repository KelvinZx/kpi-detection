import os
import torch
from config import Configuration as cfg
from src.datasets.kpi_dataloader import SingleWindowUnsupervisedKPIDataLoader
from src.lstmae.prepare_lstmae import PrepareLSTMAutoEncoder
from src.lstmae.lstm_ae import LSTMAutoEncoder
import torch.backends.cudnn as cudnn
from skorch.callbacks.lr_scheduler import WarmRestartLR
from torch.optim import SGD, Adam
from src.loss import SquareErrorLoss
import sys


MAIN_PATH = os.getcwd()
LOG_PATH = os.path.join(MAIN_PATH, 'log')


def main():
    cudnn.benchmark = True

    #args = parser.parse_args()


    print('Options:')
    for (key, value) in vars(cfg.args).items():
        print("{:16}: {}".format(key, value))


    torch.manual_seed(cfg.seed)
    ############# Model pretrain ################
        #torch.manual_seed(args.pretrain_seed)
        # Pretrain DataLoader prepare.

    lstm_ae_logger_path = os.path.join(MAIN_PATH, 'log', 'lstm_ae')

    lstmae_model = LSTMAutoEncoder(input_size=1, hidden_size=cfg.hidden_size,
                                   window_size=cfg.window_size,
                                   dropout_rate=cfg.dropout_rate, bidirectional=cfg.bidirection)
    if torch.cuda.is_available():
        print('LSTM_Auto_encoder model is running on GPU')
        lstmae_model = lstmae_model.cuda()
        torch.cuda.manual_seed(cfg.seed)

    print('LSTM_Auto_encoder Start Loading Data')
    train_loader, val_loader, test_loader = lstmae_model._load_data(SingleWindowUnsupervisedKPIDataLoader,
                                       cfg.batch_size, 1,
                                       True, True,
                                       train_datapath=os.path.join(MAIN_PATH, 'data','kpi', 'train'),
                                        test_datapath=os.path.join(MAIN_PATH, 'data','kpi', 'test'),
                                        window_size=cfg.window_size, window_gap=1)
        # _mnist_dataload(args.pretrain_mnist_normal,args.pretrain_mnist_outlier,args.pretrain_batch_size,args.workers)
    print('LSTM_Auto_encoder Finish Loading Data')


    optim = Adam(params=lstmae_model.parameters(), lr=cfg.lr)

    lstmae_model.prepare_setting(epochs=300,
                                optimizer=optim,
                                criterion=SquareErrorLoss(),
                                lr_scheduler=WarmRestartLR,
                                tensorboard_path=os.path.join(MAIN_PATH, 'tensorlog', 'lstm_ae'),
                                logger_path=lstm_ae_logger_path)

    prepare_lstm_ae_net = PrepareLSTMAutoEncoder().make_network(model=lstmae_model, train_loader=train_loader,
                                                           val_loader=val_loader, #test_loader=test_loader,
                                                             print_result_epoch=False, if_checkpoint_save=True,
                                                           print_metric_name='AUC')

    prepare_lstm_ae_net.train()


if __name__ == '__main__':
    print(sys.path)
    cfg.seed = 1234
    main()

