<?php

namespace App\actions;

use Prometheus\Storage\Redis;

class SetRedisDefaults
{
    public function handle(): void
    {
        Redis::setDefaultOptions([
            'host' => config('database.redis.default.host', '127.0.0.1'),
            'port' => config('database.redis.default.port', 6379),
            'password' => config('database.redis.default.password'),
            'database' => 2,
            'timeout' => 0.1,
            'read_timeout' => '10',
            'persistent_connections' => false
        ]);
    }
}