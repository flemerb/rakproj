.PHONY: help presentation start stop restart status health test-login test-predict clean logs open-browsers quick-check verify-all rebuild

# Colors for output
GREEN := \033[0;32m
YELLOW := \033[1;33m
RED := \033[0;31m
NC := \033[0m

help: ## Show this help message
	@echo "$(GREEN)═══════════════════════════════════════════════════════════$(NC)"
	@echo "$(GREEN)  RAKUTEN MLOPS - Makefile Commands$(NC)"
	@echo "$(GREEN)═══════════════════════════════════════════════════════════$(NC)"
	@echo ""
	@echo "$(YELLOW)Main Commands:$(NC)"
	@echo "  $(GREEN)make presentation$(NC)   - Full setup for presentation (RECOMMENDED!)"
	@echo "  $(GREEN)make quick-check$(NC)    - Quick pre-presentation verification"
	@echo "  $(GREEN)make verify-all$(NC)     - Comprehensive system check"
	@echo ""
	@echo "$(YELLOW)Service Management:$(NC)"
	@echo "  $(GREEN)make start$(NC)          - Start all services"
	@echo "  $(GREEN)make stop$(NC)           - Stop all services"
	@echo "  $(GREEN)make restart$(NC)        - Restart all services"
	@echo "  $(GREEN)make rebuild$(NC)        - Rebuild and restart"
	@echo "  $(GREEN)make clean$(NC)          - Stop and remove everything"
	@echo ""
	@echo "$(YELLOW)Testing & Monitoring:$(NC)"
	@echo "  $(GREEN)make status$(NC)         - Show service status"
	@echo "  $(GREEN)make health$(NC)         - Test health endpoints"
	@echo "  $(GREEN)make test-predict$(NC)   - Test prediction endpoint"
	@echo "  $(GREEN)make count-services$(NC) - Count running services"
	@echo "  $(GREEN)make logs$(NC)           - View service logs"
	@echo "  $(GREEN)make logs-follow$(NC)    - Follow logs in real-time"
	@echo ""
	@echo "$(YELLOW)Quick Access:$(NC)"
	@echo "  $(GREEN)make open-browsers$(NC)  - Open all dashboards in browser"
	@echo ""
	@echo "$(YELLOW)Important URLs:$(NC)"
	@echo "  Dashboard:  http://localhost:8082  (Login: admin/admin123)"
	@echo "  MLflow:     http://localhost:5000"
	@echo "  Grafana:    http://localhost:3000  (admin/admin)"
	@echo "  Airflow:    http://localhost:8081"
	@echo "  Prometheus: http://localhost:9090"
	@echo ""

presentation: ## Complete setup for presentation
	@echo "$(GREEN)╔═══════════════════════════════════════════════════════╗$(NC)"
	@echo "$(GREEN)║  PREPARING PRESENTATION - PLEASE WAIT...             ║$(NC)"
	@echo "$(GREEN)╚═══════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@echo "$(YELLOW)Stopping any running services...$(NC)"
	@docker compose down 2>/dev/null || true
	@echo "$(GREEN)[OK] Services stopped$(NC)"
	@echo ""
	@echo "$(YELLOW)Starting all services...$(NC)"
	@docker compose up -d
	@echo "$(GREEN)[OK] Services started$(NC)"
	@echo ""
	@echo "$(YELLOW)Waiting 90 seconds for services to be healthy...$(NC)"
	@sleep 90
	@echo "$(GREEN)[OK] Wait complete$(NC)"
	@echo ""
	@echo "$(YELLOW)Checking status...$(NC)"
	@docker compose ps
	@echo ""
	@echo "$(YELLOW)Testing health...$(NC)"
	@make --no-print-directory health
	@echo ""
	@echo "$(GREEN)╔═══════════════════════════════════════════════════════╗$(NC)"
	@echo "$(GREEN)║  PRESENTATION READY!                                  ║$(NC)"
	@echo "$(GREEN)╚═══════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@echo "  Dashboard: http://localhost:8082"
	@echo "  Login: admin / admin123"
	@echo ""

start: ## Start all services
	@docker compose up -d
	@echo "$(GREEN)[OK] Services started$(NC)"

stop: ## Stop all services
	@docker compose down
	@echo "$(GREEN)[OK] Services stopped$(NC)"

status: ## Show service status
	@docker compose ps

health: ## Check health endpoints
	@echo "API Gateway:"
	@curl -s http://localhost:8080/health | python3 -c "import sys, json; print('  [OK]', json.load(sys.stdin)['status'])" 2>/dev/null || echo "  [ERROR] Not responding"
	@echo "Prediction Service:"
	@curl -s http://localhost:5003/health | python3 -c "import sys, json; d=json.load(sys.stdin); print('  [OK] Model:', d['model_loaded'], 'Tokenizer:', d['tokenizer_loaded'])" 2>/dev/null || echo "  [ERROR] Not responding"

test-predict: ## Test prediction
	@TOKEN=$$(curl -s -X POST http://localhost:8080/auth/login -H "Content-Type: application/json" -d '{"username":"admin","password":"admin123"}' | python3 -c "import sys, json; print(json.load(sys.stdin).get('token', ''))"); \
	curl -s -X POST http://localhost:8080/api/v1/predict -H "Authorization: Bearer $$TOKEN" -H "Content-Type: application/json" -d '{"text":"Beautiful red dress"}' | python3 -c "import sys, json; d=json.load(sys.stdin); print('[OK] Category:', d.get('real_category'), 'Confidence:', round(d.get('confidence', 0)*100, 1), '%')" 2>/dev/null || echo "[ERROR] Failed"

open-browsers: ## Open dashboards
	@explorer.exe http://localhost:8082 2>/dev/null || true
	@sleep 1
	@explorer.exe http://localhost:5000 2>/dev/null || true
	@sleep 1
	@explorer.exe http://localhost:3000 2>/dev/null || true
	@echo "$(GREEN)[OK] Browsers opened$(NC)"

clean: ## Stop and clean everything
	@docker compose down -v
	@echo "$(GREEN)[OK] Cleaned$(NC)"

quick-check: ## Quick pre-presentation check
	@echo "$(GREEN)=== QUICK PRE-PRESENTATION CHECK ===$(NC)"
	@echo ""
	@echo "$(YELLOW)Container Status:$(NC)"
	@docker compose ps --format "table {{.Name}}\t{{.Status}}" | grep -E "(NAME|healthy)" || docker compose ps
	@echo ""
	@echo "$(YELLOW)Health Checks:$(NC)"
	@make --no-print-directory health
	@echo ""
	@echo "$(GREEN)[OK] All checks complete!$(NC)"

verify-all: ## Comprehensive system verification
	@echo "$(GREEN)=== COMPREHENSIVE VERIFICATION ===$(NC)"
	@echo ""
	@echo "$(YELLOW)1. Service Status:$(NC)"
	@docker compose ps
	@echo ""
	@echo "$(YELLOW)2. Health Endpoints:$(NC)"
	@make --no-print-directory health
	@echo ""
	@echo "$(YELLOW)3. Authentication Test:$(NC)"
	@curl -s -X POST http://localhost:8080/auth/login -H "Content-Type: application/json" -d '{"username":"admin","password":"admin123"}' | python3 -c "import sys, json; d=json.load(sys.stdin); print('  [OK] Login successful, token generated') if 'token' in d else print('  [ERROR] Login failed')" 2>/dev/null || echo "  [ERROR] Auth service not responding"
	@echo ""
	@echo "$(YELLOW)4. Prediction Test:$(NC)"
	@make --no-print-directory test-predict
	@echo ""
	@echo "$(YELLOW)5. Dashboard Access:$(NC)"
	@curl -s http://localhost:8082 > /dev/null && echo "  [OK] Dashboard accessible" || echo "  [ERROR] Dashboard not accessible"
	@echo ""
	@echo "$(GREEN)=== VERIFICATION COMPLETE ===$(NC)"

rebuild: ## Rebuild and restart all services
	@echo "$(YELLOW)Rebuilding all services...$(NC)"
	@docker compose down
	@docker compose build
	@docker compose up -d
	@echo "$(GREEN)[OK] Rebuild complete$(NC)"

logs-follow: ## Follow logs from all services
	@docker compose logs -f

count-services: ## Count running services
	@echo "$(YELLOW)Total services defined:$(NC) $$(docker compose config --services | wc -l)"
	@echo "$(YELLOW)Currently running:$(NC) $$(docker compose ps --format '{{.Name}}' | wc -l)"
	@echo "$(YELLOW)Healthy services:$(NC) $$(docker compose ps --format '{{.Status}}' | grep -c healthy || echo 0)"
