-- Adicionar chave primária na tabela combustivel, se não existir
ALTER TABLE combustivel
ADD COLUMN IF NOT EXISTS id SERIAL PRIMARY KEY;

-- Adicionar coluna combustivel_id em gastos para chave estrangeira
ALTER TABLE gastos
ADD COLUMN IF NOT EXISTS combustivel_id INTEGER;

-- Criar chave estrangeira entre gastos.combustivel_id e combustivel.id
ALTER TABLE gastos
ADD CONSTRAINT fk_combustivel
FOREIGN KEY (combustivel_id)
REFERENCES combustivel(id);
