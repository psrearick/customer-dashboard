<?php

namespace App\Providers;

use App\actions\SetRedisDefaults;
use Illuminate\Support\ServiceProvider;
use Prometheus\CollectorRegistry;
use Prometheus\RenderTextFormat;
use Prometheus\Storage\Redis;

class AppServiceProvider extends ServiceProvider
{
    /**
     * Register any application services.
     */
    public function register(): void
    {
        $this->app->singleton(CollectorRegistry::class, function () {
            app(SetRedisDefaults::class)->handle();

            return new CollectorRegistry(new Redis());
        });

        $this->app->singleton(RenderTextFormat::class);
    }

    /**
     * Bootstrap any application services.
     */
    public function boot(): void
    {
        //
    }
}
