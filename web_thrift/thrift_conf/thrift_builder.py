#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

import yaml
from thrift.protocol import TBinaryProtocol
from thrift.protocol.TMultiplexedProtocol import TMultiplexedProtocol
from thrift.server import TServer
from thrift.transport import TSocket, TTransport


class ThriftBuilder(object):
    _thrifts_config = None
    run_mode = 'development'
    _transports = {}
    yaml_path = os.path.dirname(__file__)[0:-11]

    @classmethod
    def _get_thrifts_config_by_name(cls, name='default'):
        if cls._thrifts_config is None:
            with file(os.path.join(cls.yaml_path, 'thrifts.yaml'), 'r') as file_stream:
                cls._thrifts_config = yaml.load(file_stream).get(cls.run_mode)
        thrifts_config = cls._thrifts_config.get(name)
        return thrifts_config

    @classmethod
    def _get_transport_by_name(cls, name='default'):
        thrifts_config = cls._get_thrifts_config_by_name(name)
        host = thrifts_config['host']
        port = thrifts_config['port']
        socket = TSocket.TSocket(host, port)
        transport = TTransport.TBufferedTransport(socket)
        return transport

    @classmethod
    def start_server_by_name(cls, multiplexed_processor, name='default'):
        thrifts_config = cls._get_thrifts_config_by_name(name)
        port = thrifts_config['port']
        transport = TSocket.TServerSocket(port=port)
        tfactory = TTransport.TBufferedTransportFactory()
        pfactory = TBinaryProtocol.TBinaryProtocolFactory()
        server = TServer.TThreadPoolServer(multiplexed_processor, transport, tfactory, pfactory)
        print 'Starting the thrift server at port ', port, '...'
        server.serve()

    @classmethod
    def get_client(cls, service_name, service, name="default"):
        """
        长连接不稳定,有时候会死掉,怎么解决这个问题?
        :return: SearchService.Client
        """
        old_transport = cls._transports.get(name)
        if old_transport is not None:
            old_transport.close()
        transport = cls._get_transport_by_name(name)
        cls._transports[name] = transport
        protocol = TBinaryProtocol.TBinaryProtocol(transport)
        protocol = TMultiplexedProtocol(protocol, service_name)
        service_client = service.Client(protocol)
        transport.open()
        return service_client
