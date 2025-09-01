console.log('Testing frontend connection...');

// Test basic fetch to backend
fetch('http://localhost:8000/health')
  .then(response => {
    console.log('Backend health check response:', response.status);
    return response.json();
  })
  .then(data => {
    console.log('Backend health data:', data);
  })
  .catch(error => {
    console.error('Backend connection failed:', error);
  });

// Test tool list fetch
fetch('http://localhost:8000/tools/list')
  .then(response => {
    console.log('Tools list response:', response.status);
    return response.json();
  })
  .then(data => {
    console.log('Available tools count:', data?.tools?.length || 'unknown');
    console.log('Dashboard tools found:', 
      data?.tools?.filter(t => t.name?.includes('dashboard')) || []
    );
  })
  .catch(error => {
    console.error('Tools list fetch failed:', error);
  });
