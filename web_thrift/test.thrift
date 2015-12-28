exception ThriftException {

    1: i32 error_code,
    2: string message,

}

struct ThriftTestReqBO {
    // 活动id: 之所以不采用id作为活动id的原因是因为担心别人用爬虫爬数据
    1: string thrift_string,

    // 是否允许报名
    8: bool thrift_bool,

    // 报名人数
    9: i32 thrift_32_num,

    // 报名费用
    10: double thrift_double,

}

service ThriftTestService{
    string test_thrift(1: string thrift_strings) throws (1: ThriftException e)
}
