// 확장 프로그램 에러 억제를 위한 전역 스크립트
(function() {
  'use strict';
  
  // 원래 콘솔 메서드 백업
  const originalError = console.error;
  const originalWarn = console.warn;
  const originalLog = console.log;
  
  // 필터링할 키워드들
  const filterKeywords = [
    'VDH',
    'getBasicInfo failed',
    'This video is unavailable',
    'Couldn\'t find any media',
    'youtube.js'
  ];
  
  // 메시지가 필터링되어야 하는지 확인
  function shouldFilter(message) {
    const messageStr = String(message || '');
    return filterKeywords.some(keyword => messageStr.includes(keyword));
  }
  
  // console.error 오버라이드
  console.error = function(...args) {
    if (args.length > 0 && shouldFilter(args[0])) {
      return; // 필터링된 에러는 출력하지 않음
    }
    originalError.apply(console, args);
  };
  
  // console.warn 오버라이드
  console.warn = function(...args) {
    if (args.length > 0 && shouldFilter(args[0])) {
      return; // 필터링된 경고는 출력하지 않음
    }
    originalWarn.apply(console, args);
  };
  
  // console.log 오버라이드 (일부 확장 프로그램이 log를 사용할 수 있음)
  console.log = function(...args) {
    if (args.length > 0 && shouldFilter(args[0])) {
      return; // 필터링된 로그는 출력하지 않음
    }
    originalLog.apply(console, args);
  };
  
  // 전역 에러 이벤트 리스너
  window.addEventListener('error', function(event) {
    const message = event.message || '';
    const source = event.filename || '';
    
    if (shouldFilter(message) || source.includes('youtube.js') || source.includes('extension://')) {
      event.preventDefault();
      event.stopPropagation();
      event.stopImmediatePropagation();
      return false;
    }
  }, true);
  
  // unhandledrejection 이벤트도 처리
  window.addEventListener('unhandledrejection', function(event) {
    const message = event.reason?.message || String(event.reason || '');
    
    if (shouldFilter(message)) {
      event.preventDefault();
      return false;
    }
  }, true);
  
})();