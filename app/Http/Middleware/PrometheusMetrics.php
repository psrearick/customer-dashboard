<?php

namespace App\Http\Middleware;

use App\actions\SetRedisDefaults;
use Closure;
use Exception;
use Illuminate\Http\Request;
use Log;
use Prometheus\CollectorRegistry;
use Prometheus\Storage\Redis;
use Symfony\Component\HttpFoundation\Response;

class PrometheusMetrics
{
    private CollectorRegistry $registry;
    
    public function __construct(
        SetRedisDefaults $setRedisDefaults,
    ) {
        $setRedisDefaults->handle();

        $this->registry = new CollectorRegistry(new Redis());
    }
    
    /**
     * Handle an incoming request.
     *
     * @param Closure(Request): (Response) $next
     */
    public function handle(Request $request, Closure $next): Response
    {
        $start = microtime(true);
        
        $response = $next($request);
        
        $duration = microtime(true) - $start;
        
        try {
            $counter = $this->registry->getOrRegisterCounter(
                'laravel',
                'http_requests_total',
                'Total HTTP requests',
                ['method', 'route', 'status']
            );
            
            $histogram = $this->registry->getOrRegisterHistogram(
                'laravel',
                'http_request_duration_seconds',
                'HTTP request duration in seconds',
                ['method', 'route', 'status'],
                [0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10]
            );
            
            $route = $request->route() ? $request->route()->uri() : 'unknown';
            $method = $request->method();
            $status = $response->getStatusCode();
            
            $counter->incBy(1, [$method, $route, (string)$status]);
            $histogram->observe($duration, [$method, $route, (string)$status]);
            
        } catch (Exception $e) {
            Log::error('Prometheus metrics error: ' . $e->getMessage());
        }
        
        return $response;
    }
}