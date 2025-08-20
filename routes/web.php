<?php

use App\Http\Controllers\MetricsController;
use Illuminate\Support\Facades\Route;
use Inertia\Inertia;

Route::get('/', function () {
    return Inertia::render('Welcome');
})->name('home');

Route::get('/dashboard', function () {
    return Inertia::render('Dashboard');
})->name('dashboard');

Route::get('/contact', function () {
    return Inertia::render('ContactForm');
})->name('contact.form');

Route::post('/contact', function () {
    request()->validate([
        'name' => 'required|string|max:255',
        'email' => 'required|email|max:255',
        'subject' => 'required|string|max:255',
        'message' => 'required|string|min:10',
    ]);
    
    session()->flash('success', 'Your message has been sent successfully!');
    
    return redirect()->back();
})->name('contact.submit');

Route::get('/status', function () {
    return response()->json([
        'status' => 'ok',
        'timestamp' => now()->toISOString(),
        'laravel' => app()->version(),
    ]);
});

Route::get('/metrics', [MetricsController::class, 'metrics']);
